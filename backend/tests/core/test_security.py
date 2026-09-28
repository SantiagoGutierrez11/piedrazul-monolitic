"""Pruebas de la validación de tokens y del control de acceso por rol."""
import pytest

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.security import CurrentUser, Role, TokenVerifier
from tests.auth_helpers import TokenFactory

WINDOW_URL = "/api/v1/configuration/global/appointment-window"


def _bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------- TokenVerifier


def test_valid_token_returns_user_with_known_roles(token_factory):
    token = token_factory.token(
        roles=["agendador", "offline_access"], sub="abc", email="ana@piedrazul.com", name="Ana Ruiz"
    )

    user = token_factory.verifier().verify(token)

    assert user == CurrentUser(
        user_id="abc",
        email="ana@piedrazul.com",
        full_name="Ana Ruiz",
        roles=frozenset({Role.AGENDADOR}),
    )


def test_expired_token_is_rejected(token_factory):
    with pytest.raises(AuthenticationError, match="expiró"):
        token_factory.verifier().verify(token_factory.token(expires_in=-60))


@pytest.mark.parametrize(
    "claims",
    [
        {"issuer": "http://otro-servidor/realms/piedrazul"},
        {"audience": "otro-cliente"},
    ],
    ids=["otro-emisor", "otra-audiencia"],
)
def test_token_for_another_issuer_or_audience_is_rejected(token_factory, claims):
    with pytest.raises(AuthenticationError):
        token_factory.verifier().verify(token_factory.token(**claims))


def test_token_signed_with_another_key_is_rejected(token_factory):
    impostor = TokenFactory(kid=token_factory.kid)

    with pytest.raises(AuthenticationError):
        token_factory.verifier().verify(impostor.token())


def test_token_without_subject_is_rejected(token_factory):
    with pytest.raises(AuthenticationError):
        token_factory.verifier().verify(token_factory.token(sub=""))


def test_malformed_token_is_rejected(token_factory):
    with pytest.raises(AuthenticationError):
        token_factory.verifier().verify("no-es-un-jwt")


def test_unknown_key_reloads_keys_once_before_rejecting(token_factory):
    fetches = []

    def fetch_jwks():
        fetches.append(1)
        return {"keys": [token_factory.jwk]}

    verifier = TokenVerifier(settings.keycloak_issuer, settings.keycloak_client_id, fetch_jwks)
    verifier.verify(token_factory.token())
    verifier.verify(token_factory.token())

    with pytest.raises(AuthenticationError):
        verifier.verify(token_factory.token(kid="llave-rotada"))

    assert len(fetches) == 2


# ---------------------------------------------------------------- Rutas protegidas


def test_request_without_token_is_rejected(real_tokens, client):
    response = client.get("/api/v1/medical/doctors")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_role_without_permission_is_forbidden(real_tokens, client):
    token = real_tokens.token(roles=["agendador"])

    response = client.put(WINDOW_URL, json={"weeks": 6}, headers=_bearer(token))

    assert response.status_code == 403
    assert response.json() == {"message": "No tienes permiso para realizar esta operación"}


def test_administrator_can_update_configuration(real_tokens, client):
    token = real_tokens.token(roles=["administrador"])

    response = client.put(WINDOW_URL, json={"weeks": 6}, headers=_bearer(token))

    assert response.status_code == 200
    assert response.json() == {"weeks": 6}


def test_any_authenticated_role_can_read_configuration(client, login_as):
    login_as(Role.PACIENTE)

    assert client.get("/api/v1/configuration/global").status_code == 200


def test_patient_cannot_list_a_doctor_agenda(client, login_as):
    login_as(Role.PACIENTE)

    assert client.get("/api/v1/appointments/doctor/1/date/2026-03-10").status_code == 403
