"""
Seguridad transversal: valida los tokens que emite Keycloak y expone el usuario autenticado.

Los módulos protegen sus rutas con `require_role(Role.X, ...)` o `get_current_user`; ninguno
valida tokens por su cuenta.
"""
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum

import httpx
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ForbiddenError, ServiceUnavailableError


class Role(str, Enum):
    """Roles del realm `piedrazul` en Keycloak."""

    PACIENTE = "paciente"
    AGENDADOR = "agendador"
    MEDICO = "medico"
    ADMINISTRADOR = "administrador"


@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    email: str
    full_name: str
    roles: frozenset[Role]

    def has_any(self, roles: Iterable[Role]) -> bool:
        return not self.roles.isdisjoint(roles)

    @classmethod
    def from_claims(cls, claims: dict) -> "CurrentUser":
        known = {role.value for role in Role}
        realm_roles = claims.get("realm_access", {}).get("roles", [])
        full_name = claims.get("name") or " ".join(
            part for part in (claims.get("given_name"), claims.get("family_name")) if part
        )
        return cls(
            user_id=claims["sub"],
            email=claims.get("email", ""),
            full_name=full_name or claims.get("preferred_username", ""),
            roles=frozenset(Role(role) for role in realm_roles if role in known),
        )


class TokenVerifier:
    """Valida firma RS256 (llaves públicas del realm), emisor, audiencia y expiración."""

    def __init__(self, issuer: str, audience: str, fetch_jwks: Callable[[], dict]):
        self._issuer = issuer
        self._audience = audience
        self._fetch_jwks = fetch_jwks
        self._keys: dict[str, dict] = {}

    def verify(self, token: str) -> CurrentUser:
        try:
            kid = jwt.get_unverified_header(token).get("kid")
        except JWTError as exc:
            raise AuthenticationError("Token inválido") from exc

        try:
            claims = jwt.decode(
                token,
                self._key_for(kid),
                algorithms=["RS256"],
                audience=self._audience,
                issuer=self._issuer,
            )
        except ExpiredSignatureError as exc:
            raise AuthenticationError("La sesión expiró, vuelve a iniciar sesión") from exc
        except JWTError as exc:
            raise AuthenticationError("Token inválido") from exc

        if not claims.get("sub"):
            raise AuthenticationError("Token inválido")
        return CurrentUser.from_claims(claims)

    def _key_for(self, kid: str | None) -> dict:
        if kid not in self._keys:
            # Llave desconocida: Keycloak pudo rotarlas, así que se recargan antes de rechazar.
            self._keys = {key["kid"]: key for key in self._fetch_jwks().get("keys", [])}
        if kid not in self._keys:
            raise AuthenticationError("Token inválido")
        return self._keys[kid]


def _fetch_keycloak_jwks() -> dict:
    url = f"{settings.keycloak_issuer}/protocol/openid-connect/certs"
    try:
        response = httpx.get(url, timeout=5)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ServiceUnavailableError("El servicio de autenticación no está disponible") from exc
    return response.json()


_token_verifier = TokenVerifier(
    issuer=settings.keycloak_issuer,
    audience=settings.keycloak_client_id,
    fetch_jwks=_fetch_keycloak_jwks,
)


def get_token_verifier() -> TokenVerifier:
    return _token_verifier


_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    verifier: TokenVerifier = Depends(get_token_verifier),
) -> CurrentUser:
    if credentials is None:
        raise AuthenticationError("No autenticado")
    return verifier.verify(credentials.credentials)


def require_role(*roles: Role):
    """Dependencia que exige al menos uno de los roles indicados."""

    def _checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not user.has_any(roles):
            raise ForbiddenError("No tienes permiso para realizar esta operación")
        return user

    return _checker
