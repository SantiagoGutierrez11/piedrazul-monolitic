"""Puerto hacia el proveedor de identidad; la implementación concreta vive en infrastructure/."""
from abc import ABC, abstractmethod

from app.core.security import Role
from app.modules.identity.domain.entities import NewUser, TokenSet


class IdentityProvider(ABC):
    @abstractmethod
    def authenticate(self, email: str, password: str) -> TokenSet:
        """Lanza AuthenticationError si las credenciales no son válidas."""

    @abstractmethod
    def refresh(self, refresh_token: str) -> TokenSet:
        """Lanza AuthenticationError si la sesión ya no es válida."""

    @abstractmethod
    def logout(self, refresh_token: str) -> None: ...

    @abstractmethod
    def create_user(self, user: NewUser, role: Role) -> str:
        """Crea el usuario con el rol indicado y devuelve su identificador."""

    @abstractmethod
    def delete_user(self, user_id: str) -> None: ...
