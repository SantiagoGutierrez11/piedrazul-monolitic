"""Montado bajo /api/v1/auth (ver app/main.py)."""
from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, TokenVerifier, get_current_user, get_token_verifier
from app.modules.identity.api.schemas import (
    LoginRequest,
    RefreshRequest,
    SessionResponse,
    UserResponse,
)
from app.modules.identity.application.auth_service import AuthService
from app.modules.identity.domain.ports import IdentityProvider
from app.modules.identity.infrastructure.keycloak_provider import get_identity_provider

router = APIRouter()


def get_auth_service(
    provider: IdentityProvider = Depends(get_identity_provider),
    verifier: TokenVerifier = Depends(get_token_verifier),
) -> AuthService:
    return AuthService(provider, verifier)


@router.post("/login", response_model=SessionResponse)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)):
    return SessionResponse.from_session(service.login(payload.email, payload.password))


@router.post("/refresh", response_model=SessionResponse)
def refresh(payload: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    return SessionResponse.from_session(service.refresh(payload.refresh_token))


@router.post("/logout", status_code=204)
def logout(payload: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    service.logout(payload.refresh_token)


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUser = Depends(get_current_user)):
    return UserResponse.from_user(user)
