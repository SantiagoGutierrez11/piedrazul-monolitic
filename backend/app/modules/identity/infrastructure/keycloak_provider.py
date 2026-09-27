"""Implementación del proveedor de identidad sobre la API de Keycloak."""
import time
from functools import lru_cache

import httpx

from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    ServiceUnavailableError,
    ValidationError,
)
from app.core.security import Role
from app.modules.identity.domain.entities import NewUser, TokenSet
from app.modules.identity.domain.ports import IdentityProvider

UNAVAILABLE = "El servicio de autenticación no está disponible"


class KeycloakIdentityProvider(IdentityProvider):
    def __init__(
        self,
        base_url: str,
        realm: str,
        client_id: str,
        client_secret: str,
        http: httpx.Client | None = None,
    ):
        self._token_url = f"{base_url}/realms/{realm}/protocol/openid-connect/token"
        self._logout_url = f"{base_url}/realms/{realm}/protocol/openid-connect/logout"
        self._admin_url = f"{base_url}/admin/realms/{realm}"
        self._client = {"client_id": client_id, "client_secret": client_secret}
        self._http = http or httpx.Client(timeout=10)
        self._service_token: str | None = None
        self._service_token_expires_at = 0.0

    # ------------------------------------------------------------------ sesiones

    def authenticate(self, email: str, password: str) -> TokenSet:
        response = self._send(
            "POST",
            self._token_url,
            data={**self._client, "grant_type": "password", "username": email, "password": password},
        )
        if response.status_code in (400, 401) and _oauth_field(response, "error") == "invalid_grant":
            if "disabled" in _oauth_field(response, "error_description").lower():
                raise AuthenticationError("La cuenta está deshabilitada")
            raise AuthenticationError("Correo o contraseña incorrectos")
        return _token_set(self._ensure_ok(response))

    def refresh(self, refresh_token: str) -> TokenSet:
        response = self._send(
            "POST",
            self._token_url,
            data={**self._client, "grant_type": "refresh_token", "refresh_token": refresh_token},
        )
        if response.status_code in (400, 401) and _oauth_field(response, "error") == "invalid_grant":
            raise AuthenticationError("La sesión expiró, vuelve a iniciar sesión")
        return _token_set(self._ensure_ok(response))

    def logout(self, refresh_token: str) -> None:
        # Si la sesión ya no existe en Keycloak no hay nada que cerrar: no se valida la respuesta.
        self._send("POST", self._logout_url, data={**self._client, "refresh_token": refresh_token})

    # ------------------------------------------------------------------ usuarios

    def create_user(self, user: NewUser, role: Role) -> str:
        response = self._admin(
            "POST",
            "/users",
            json={
                "username": user.email,
                "email": user.email,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "enabled": True,
                "emailVerified": False,
                "credentials": [{"type": "password", "value": user.password, "temporary": False}],
            },
        )
        if response.status_code == 409:
            raise ConflictError("Ya existe una cuenta registrada con ese correo electrónico")
        if response.status_code == 400:
            if "password" in response.text.lower():
                raise ValidationError("La contraseña debe tener mínimo 8 caracteres")
            raise ValidationError("Los datos de la cuenta no son válidos")
        self._ensure_ok(response)

        user_id = response.headers["Location"].rstrip("/").rsplit("/", 1)[-1]
        try:
            self._assign_realm_role(user_id, role)
        except Exception:
            # Un usuario sin rol no podría usar el sistema: se deshace la creación.
            self.delete_user(user_id)
            raise
        return user_id

    def delete_user(self, user_id: str) -> None:
        response = self._admin("DELETE", f"/users/{user_id}")
        if response.status_code != 404:
            self._ensure_ok(response)

    def _assign_realm_role(self, user_id: str, role: Role) -> None:
        role_representation = self._ensure_ok(self._admin("GET", f"/roles/{role.value}")).json()
        self._ensure_ok(
            self._admin("POST", f"/users/{user_id}/role-mappings/realm", json=[role_representation])
        )

    # ------------------------------------------------------------------ HTTP

    def _admin(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Llama a la API de administración con el token de la cuenta de servicio del backend."""
        response = self._send_admin(method, path, self._get_service_token(), **kwargs)
        if response.status_code == 401:
            # El token cacheado pudo invalidarse antes de vencer: se pide uno nuevo una sola vez.
            response = self._send_admin(method, path, self._get_service_token(force=True), **kwargs)
        return response

    def _send_admin(self, method: str, path: str, token: str, **kwargs) -> httpx.Response:
        headers = {"Authorization": f"Bearer {token}"}
        return self._send(method, f"{self._admin_url}{path}", headers=headers, **kwargs)

    def _get_service_token(self, force: bool = False) -> str:
        if force or self._service_token is None or time.monotonic() >= self._service_token_expires_at:
            response = self._send(
                "POST", self._token_url, data={**self._client, "grant_type": "client_credentials"}
            )
            body = self._ensure_ok(response).json()
            self._service_token = body["access_token"]
            # Margen de 30 s para no usar un token a punto de vencer.
            self._service_token_expires_at = time.monotonic() + body.get("expires_in", 60) - 30
        return self._service_token

    def _send(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            return self._http.request(method, url, **kwargs)
        except httpx.HTTPError as exc:
            raise ServiceUnavailableError(UNAVAILABLE) from exc

    @staticmethod
    def _ensure_ok(response: httpx.Response) -> httpx.Response:
        if response.is_error:
            raise ServiceUnavailableError(UNAVAILABLE)
        return response


def _token_set(response: httpx.Response) -> TokenSet:
    body = response.json()
    return TokenSet(
        access_token=body["access_token"],
        refresh_token=body["refresh_token"],
        expires_in=body["expires_in"],
        refresh_expires_in=body.get("refresh_expires_in", 0),
    )


def _oauth_field(response: httpx.Response, field: str) -> str:
    try:
        return str(response.json().get(field, ""))
    except ValueError:
        return ""


@lru_cache
def get_identity_provider() -> IdentityProvider:
    return KeycloakIdentityProvider(
        base_url=settings.keycloak_url,
        realm=settings.keycloak_realm,
        client_id=settings.keycloak_client_id,
        client_secret=settings.keycloak_client_secret,
    )
