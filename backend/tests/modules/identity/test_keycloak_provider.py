"""Pruebas del adaptador de Keycloak contra un servidor simulado (sin red)."""
import json
from urllib.parse import parse_qsl

import httpx
import pytest

from app.core.exceptions import AuthenticationError, ConflictError, ServiceUnavailableError
from app.core.security import Role
from app.modules.identity.domain.entities import NewUser
from app.modules.identity.infrastructure.keycloak_provider import KeycloakIdentityProvider

BASE = "http://keycloak.test"
TOKEN_PATH = "/realms/piedrazul/protocol/openid-connect/token"
ADMIN = "/admin/realms/piedrazul"
NEW_USER = NewUser(
    email="maria@correo.com", password="clave1234", first_name="María Fernanda", last_name="Gómez"
)
TOKENS = {"access_token": "acceso", "refresh_token": "renovacion", "expires_in": 300, "refresh_expires_in": 1800}


class FakeKeycloak:
    """Responde como Keycloak y registra cada petición recibida."""

    def __init__(self, responses: dict[tuple[str, str], httpx.Response]):
        self._responses = responses
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        grant = dict(parse_qsl(request.content.decode())).get("grant_type")
        if request.url.path == TOKEN_PATH and grant == "client_credentials":
            return httpx.Response(200, json={"access_token": "token-servicio", "expires_in": 300})
        return self._responses[(request.method, request.url.path)]

    def calls(self, method: str, path: str) -> list[httpx.Request]:
        return [r for r in self.requests if r.method == method and r.url.path == path]

    def service_token_requests(self) -> int:
        return sum(
            1
            for r in self.requests
            if r.url.path == TOKEN_PATH
            and dict(parse_qsl(r.content.decode())).get("grant_type") == "client_credentials"
        )


def _provider(keycloak) -> KeycloakIdentityProvider:
    http = httpx.Client(transport=httpx.MockTransport(keycloak))
    return KeycloakIdentityProvider(BASE, "piedrazul", "piedrazul-backend", "secreto", http=http)


def _creating_user(role_mapping=None) -> FakeKeycloak:
    return FakeKeycloak(
        {
            ("POST", f"{ADMIN}/users"): httpx.Response(
                201, headers={"Location": f"{BASE}{ADMIN}/users/kc-123"}
            ),
            ("GET", f"{ADMIN}/roles/paciente"): httpx.Response(200, json={"id": "r1", "name": "paciente"}),
            ("POST", f"{ADMIN}/users/kc-123/role-mappings/realm"): role_mapping or httpx.Response(204),
            ("DELETE", f"{ADMIN}/users/kc-123"): httpx.Response(204),
        }
    )


def test_authenticate_uses_password_grant_with_backend_client():
    keycloak = FakeKeycloak({("POST", TOKEN_PATH): httpx.Response(200, json=TOKENS)})

    tokens = _provider(keycloak).authenticate("maria@correo.com", "clave1234")

    form = dict(parse_qsl(keycloak.requests[0].content.decode()))
    assert form == {
        "client_id": "piedrazul-backend",
        "client_secret": "secreto",
        "grant_type": "password",
        "username": "maria@correo.com",
        "password": "clave1234",
    }
    assert (tokens.access_token, tokens.refresh_token, tokens.expires_in) == ("acceso", "renovacion", 300)


def test_authenticate_with_wrong_credentials_raises_authentication_error():
    keycloak = FakeKeycloak(
        {("POST", TOKEN_PATH): httpx.Response(401, json={"error": "invalid_grant", "error_description": "Invalid user credentials"})}
    )

    with pytest.raises(AuthenticationError, match="Correo o contraseña incorrectos"):
        _provider(keycloak).authenticate("maria@correo.com", "equivocada")


def test_create_user_registers_account_and_assigns_role():
    keycloak = _creating_user()

    user_id = _provider(keycloak).create_user(NEW_USER, Role.PACIENTE)

    assert user_id == "kc-123"
    payload = json.loads(keycloak.calls("POST", f"{ADMIN}/users")[0].content)
    assert payload["username"] == payload["email"] == "maria@correo.com"
    assert (payload["firstName"], payload["lastName"]) == ("María Fernanda", "Gómez")
    assert payload["credentials"] == [{"type": "password", "value": "clave1234", "temporary": False}]
    mapping = keycloak.calls("POST", f"{ADMIN}/users/kc-123/role-mappings/realm")[0]
    assert json.loads(mapping.content) == [{"id": "r1", "name": "paciente"}]
    assert mapping.headers["Authorization"] == "Bearer token-servicio"


def test_create_user_with_existing_email_raises_conflict():
    keycloak = FakeKeycloak({("POST", f"{ADMIN}/users"): httpx.Response(409, json={"errorMessage": "User exists"})})

    with pytest.raises(ConflictError):
        _provider(keycloak).create_user(NEW_USER, Role.PACIENTE)

    assert not keycloak.calls("GET", f"{ADMIN}/roles/paciente")


def test_user_is_deleted_when_role_cannot_be_assigned():
    keycloak = _creating_user(role_mapping=httpx.Response(500))

    with pytest.raises(ServiceUnavailableError):
        _provider(keycloak).create_user(NEW_USER, Role.PACIENTE)

    assert len(keycloak.calls("DELETE", f"{ADMIN}/users/kc-123")) == 1


def test_service_token_is_reused_between_admin_calls():
    keycloak = _creating_user()
    provider = _provider(keycloak)

    provider.create_user(NEW_USER, Role.PACIENTE)
    provider.delete_user("kc-123")

    assert keycloak.service_token_requests() == 1


def test_unreachable_keycloak_raises_service_unavailable():
    def offline(request):
        raise httpx.ConnectError("sin conexión", request=request)

    with pytest.raises(ServiceUnavailableError):
        _provider(offline).authenticate("maria@correo.com", "clave1234")
