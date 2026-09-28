"""DTOs de autenticación."""
from pydantic import Field

from app.core.security import CurrentUser, Role
from app.modules.identity.application.auth_service import AuthSession
from app.shared.schemas import CamelModel


class LoginRequest(CamelModel):
    email: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(CamelModel):
    refresh_token: str = Field(min_length=1)


class UserResponse(CamelModel):
    id: str
    email: str
    full_name: str
    roles: list[Role]

    @classmethod
    def from_user(cls, user: CurrentUser) -> "UserResponse":
        return cls(
            id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            roles=sorted(user.roles, key=lambda role: role.value),
        )


class SessionResponse(CamelModel):
    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int
    user: UserResponse

    @classmethod
    def from_session(cls, session: AuthSession) -> "SessionResponse":
        return cls(
            access_token=session.tokens.access_token,
            refresh_token=session.tokens.refresh_token,
            expires_in=session.tokens.expires_in,
            refresh_expires_in=session.tokens.refresh_expires_in,
            user=UserResponse.from_user(session.user),
        )
