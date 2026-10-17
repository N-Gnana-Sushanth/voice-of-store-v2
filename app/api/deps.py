"""API dependencies: authentication, RBAC, and store-level authorization."""

from typing import Callable, List, Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.models.user import User, UserRole

# HTTP Bearer scheme
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate Bearer JWT and retrieve authenticated active user."""
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Missing Authorization header or Bearer token")

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except ValueError as e:
        raise AuthenticationError(str(e))

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Token payload missing subject identifier")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AuthenticationError("Authenticated user no longer exists")

    if not user.is_active:
        raise AuthorizationError("User account is inactive or disabled")

    return user


def require_roles(allowed_roles: List[str]) -> Callable[[User], User]:
    """Dependency factory checking that user holds one of the allowed roles."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AuthorizationError(
                f"Role '{current_user.role}' is not authorized for this operation. "
                f"Required one of: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker


def check_store_access(user: User, store_id: str) -> None:
    """
    Enforces store-level data isolation.
    - Admin & Analyst: global access.
    - Store Manager: restricted strictly to their assigned store.
    """
    if user.role in [UserRole.ADMIN, UserRole.ANALYST]:
        return

    if user.role == UserRole.STORE_MANAGER:
        if not user.store_id or user.store_id != store_id:
            raise AuthorizationError(
                f"Store manager is restricted to their assigned store and cannot access store '{store_id}'."
            )
        return

    raise AuthorizationError("Access denied to store records.")
