"""API v1 master router mounting all service endpoints."""

from fastapi import APIRouter
from app.api.v1.alerts import router as alerts_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.health import router as health_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.precision import router as precision_router
from app.api.v1.regional_briefs import router as regional_briefs_router
from app.api.v1.replay import router as replay_router
from app.api.v1.routing import router as routing_router
from app.api.v1.stores import router as stores_router
from app.api.v1.tasks import router as tasks_router

api_v1_router = APIRouter()

# Mount health & readiness directly at root or under v1
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(stores_router)
api_v1_router.include_router(feedback_router)
api_v1_router.include_router(incidents_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(alerts_router)
api_v1_router.include_router(replay_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(tasks_router)
api_v1_router.include_router(regional_briefs_router)
api_v1_router.include_router(routing_router)
api_v1_router.include_router(precision_router)
