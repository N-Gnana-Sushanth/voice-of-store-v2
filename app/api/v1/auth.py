"""Authentication and user management API endpoints."""

from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db, require_roles
from app.core.config import settings
from app.core.exceptions import AuthenticationError, DuplicateEntityError, InvalidInputError
from app.core.middleware import rate_limiter
from app.core.security import create_access_token, hash_password, verify_password
from app.models.audit import AuditAction
from app.models.store import Store
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.services.audit_service import audit_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="User Login")
def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate with email and password to receive a signed JWT access token."""
    client_ip = request.client.host if request.client else "unknown"
    allowed, retry_after = rate_limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise AuthenticationError("Invalid email or password.")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    # Issue token
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=user.id,
        role=user.role,
        store_id=user.store_id,
        expires_delta=expires,
        custom_claims={"email": user.email, "name": user.full_name},
    )

    # Audit login
    audit_service.log_event(
        db=db,
        action=AuditAction.USER_LOGIN,
        resource_type="User",
        resource_id=user.id,
        actor=user,
        details={"ip": client_ip},
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse, summary="Get Current Authenticated User")
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Retrieve identity and permissions for the currently authenticated caller."""
    return UserResponse.model_validate(current_user)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User (Admin Only)",
)
def create_user(
    user_in: UserCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Admin-only endpoint to provision users with designated roles."""
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise DuplicateEntityError("User", user_in.email, f"User with email '{user_in.email}' already exists.")

    if user_in.role not in UserRole.ALL:
        raise InvalidInputError(f"Invalid role '{user_in.role}'. Allowed: {UserRole.ALL}")

    if user_in.role == UserRole.STORE_MANAGER and not user_in.store_id:
        raise InvalidInputError("store_id is required when creating a store_manager user.")

    if user_in.store_id:
        store = db.query(Store).filter(Store.id == user_in.store_id).first()
        if not store:
            raise InvalidInputError(f"Target store '{user_in.store_id}' does not exist.")

    new_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        store_id=user_in.store_id,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    audit_service.log_event(
        db=db,
        action="USER_CREATED",
        resource_type="User",
        resource_id=new_user.id,
        actor=current_user,
        details={"role": new_user.role, "email": new_user.email},
    )

    return UserResponse.model_validate(new_user)
