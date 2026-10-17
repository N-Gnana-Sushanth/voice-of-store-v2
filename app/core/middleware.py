"""Application middleware: correlation ID, request limits, and security headers."""

import time
import uuid
from typing import Dict, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import settings
from app.core.logging import correlation_id_ctx, logger


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns and propagates request correlation IDs."""

    async def dispatch(self, request: Request, call_next):
        corr_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        token = correlation_id_ctx.set(corr_id)
        start_time = time.perf_counter()

        try:
            response: Response = await call_next(request)
            process_time = time.perf_counter() - start_time
            response.headers["X-Correlation-ID"] = corr_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}s"
            return response
        finally:
            correlation_id_ctx.reset(token)


class SecurityAndLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for body size checks and standard security headers."""

    async def dispatch(self, request: Request, call_next):
        # 1. Check content-length for request size abuse
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > settings.MAX_REQUEST_BODY_BYTES:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": {
                                "code": "PAYLOAD_TOO_LARGE",
                                "message": f"Request body exceeds maximum allowed size of {settings.MAX_REQUEST_BODY_BYTES} bytes.",
                                "details": {"max_bytes": settings.MAX_REQUEST_BODY_BYTES, "received_bytes": length},
                            }
                        },
                    )
            except ValueError:
                pass

        # 2. Process request
        response: Response = await call_next(request)

        # 3. Add standard security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class SimpleRateLimiter:
    """In-memory sliding-window rate limiter for sensitive endpoints (e.g., login)."""

    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        # client_ip -> list of timestamps
        self.records: Dict[str, list] = {}

    def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        now = time.time()
        window_start = now - 60.0

        timestamps = self.records.get(client_id, [])
        # Prune older than 1 minute
        timestamps = [t for t in timestamps if t > window_start]
        self.records[client_id] = timestamps

        if len(timestamps) >= self.rpm:
            retry_after = int(60.0 - (now - timestamps[0]))
            return False, max(retry_after, 1)

        timestamps.append(now)
        return True, 0


rate_limiter = SimpleRateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)
