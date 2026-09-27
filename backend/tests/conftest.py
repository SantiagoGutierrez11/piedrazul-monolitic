"""Fixtures compartidas: base de datos SQLite en memoria, cliente HTTP de pruebas y autenticación."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import CurrentUser, Role, get_current_user, get_token_verifier
from app.main import app
from app.modules.identity.infrastructure.keycloak_provider import get_identity_provider
from tests.auth_helpers import FakeIdentityProvider, TokenFactory


def _user(*roles: Role, user_id: str = "usuario-pruebas") -> CurrentUser:
    return CurrentUser(
        user_id=user_id,
        email="pruebas@piedrazul.com",
        full_name="Usuario de Pruebas",
        roles=frozenset(roles),
    )


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    # Sin context manager: no dispara el lifespan, así las pruebas nunca tocan la BD de desarrollo.
    app.dependency_overrides[get_db] = lambda: db_session
    # Por defecto se actúa con un usuario que tiene todos los roles; las pruebas de autorización
    # lo cambian con `login_as` o validan tokens reales con `real_tokens`.
    app.dependency_overrides[get_current_user] = lambda: _user(*Role)
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def login_as(client):
    def _login_as(*roles: Role, user_id: str = "usuario-pruebas") -> CurrentUser:
        user = _user(*roles, user_id=user_id)
        app.dependency_overrides[get_current_user] = lambda: user
        return user

    return _login_as


@pytest.fixture(scope="session")
def token_factory():
    return TokenFactory()


@pytest.fixture()
def real_tokens(client, token_factory):
    """Las peticiones se autentican validando tokens firmados, como en producción."""
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides[get_token_verifier] = token_factory.verifier
    return token_factory


@pytest.fixture()
def identity_provider(real_tokens):
    provider = FakeIdentityProvider(real_tokens)
    app.dependency_overrides[get_identity_provider] = lambda: provider
    return provider
