"""Dobles de prueba para autenticación: tokens firmados localmente y un proveedor de identidad en memoria."""
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwk, jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import Role, TokenVerifier
from app.modules.identity.domain.entities import NewUser, TokenSet
from app.modules.identity.domain.ports import IdentityProvider


class TokenFactory:
    """Firma tokens con la misma forma que los de Keycloak, usando una llave RSA local."""

    def __init__(self, kid: str = "llave-de-pruebas"):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self._private_pem = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        public_pem = key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.kid = kid
        self.jwk = {**jwk.construct(public_pem, "RS256").to_dict(), "kid": kid, "use": "sig"}

    def token(
        self,
        roles=(Role.PACIENTE.value,),
        *,
        sub: str = "usuario-1",
        email: str = "usuario@piedrazul.com",
        name: str = "Usuario Prueba",
        issuer: str = settings.keycloak_issuer,
        audience: str = settings.keycloak_client_id,
        expires_in: int = 300,
        kid: str | None = None,
    ) -> str:
        now = int(time.time())
        claims = {
            "sub": sub,
            "email": email,
            "name": name,
            "iss": issuer,
            "aud": audience,
            "iat": now,
            "exp": now + expires_in,
            "realm_access": {"roles": list(roles)},
        }
        return jwt.encode(claims, self._private_pem, algorithm="RS256", headers={"kid": kid or self.kid})

    def verifier(self) -> TokenVerifier:
        return TokenVerifier(
            issuer=settings.keycloak_issuer,
            audience=settings.keycloak_client_id,
            fetch_jwks=lambda: {"keys": [self.jwk]},
        )


class FakeIdentityProvider(IdentityProvider):
    """Keycloak en memoria: guarda usuarios y emite tokens firmados por TokenFactory."""

    def __init__(self, tokens: TokenFactory):
        self._tokens = tokens
        self.users: dict[str, tuple[NewUser, Role]] = {}
        self.deleted: list[str] = []
        self.logged_out: list[str] = []
        self.fail_create_with: Exception | None = None

    def add_user(self, email: str, password: str, role: Role, first_name="Usuario", last_name="Prueba") -> str:
        return self.create_user(NewUser(email, password, first_name, last_name), role)

    def create_user(self, user: NewUser, role: Role) -> str:
        if self.fail_create_with:
            raise self.fail_create_with
        if any(existing.email == user.email for existing, _ in self.users.values()):
            raise ConflictError("Ya existe una cuenta registrada con ese correo electrónico")
        user_id = f"kc-{len(self.users) + len(self.deleted) + 1}"
        self.users[user_id] = (user, role)
        return user_id

    def delete_user(self, user_id: str) -> None:
        self.deleted.append(user_id)
        self.users.pop(user_id, None)

    def authenticate(self, email: str, password: str) -> TokenSet:
        for user_id, (user, role) in self.users.items():
            if user.email == email and user.password == password:
                return self._issue(user_id)
        raise AuthenticationError("Correo o contraseña incorrectos")

    def refresh(self, refresh_token: str) -> TokenSet:
        user_id = refresh_token.removeprefix("refresh-")
        if user_id not in self.users:
            raise AuthenticationError("La sesión expiró, vuelve a iniciar sesión")
        return self._issue(user_id)

    def logout(self, refresh_token: str) -> None:
        self.logged_out.append(refresh_token)

    def _issue(self, user_id: str) -> TokenSet:
        user, role = self.users[user_id]
        access = self._tokens.token(
            roles=[role.value],
            sub=user_id,
            email=user.email,
            name=f"{user.first_name} {user.last_name}",
        )
        return TokenSet(access_token=access, refresh_token=f"refresh-{user_id}", expires_in=300, refresh_expires_in=1800)
