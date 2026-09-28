"""Casos de uso de sesión: iniciar, renovar y cerrar."""
from dataclasses import dataclass

from app.core.security import CurrentUser, TokenVerifier
from app.modules.identity.domain.entities import TokenSet
from app.modules.identity.domain.ports import IdentityProvider


@dataclass(frozen=True)
class AuthSession:
    tokens: TokenSet
    user: CurrentUser


class AuthService:
    def __init__(self, provider: IdentityProvider, verifier: TokenVerifier):
        self._provider = provider
        self._verifier = verifier

    def login(self, email: str, password: str) -> AuthSession:
        return self._session(self._provider.authenticate(email.strip().lower(), password))

    def refresh(self, refresh_token: str) -> AuthSession:
        return self._session(self._provider.refresh(refresh_token))

    def logout(self, refresh_token: str) -> None:
        self._provider.logout(refresh_token)

    def _session(self, tokens: TokenSet) -> AuthSession:
        # Se valida el token recién emitido: el cliente recibe exactamente los datos y roles
        # que el backend exigirá en cada petición.
        return AuthSession(tokens=tokens, user=self._verifier.verify(tokens.access_token))
