"""
Interfaz pública del módulo `identity` para el resto del monolito.

Los demás módulos crean o eliminan cuentas de acceso solo a través de esta clase.
"""
from app.core.security import Role
from app.modules.identity.domain.entities import NewUser
from app.modules.identity.domain.ports import IdentityProvider


class AccountDirectory:
    def __init__(self, provider: IdentityProvider):
        self._provider = provider

    def create_patient_account(self, email: str, password: str, first_name: str, last_name: str) -> str:
        return self._provider.create_user(
            NewUser(email=email, password=password, first_name=first_name, last_name=last_name),
            Role.PACIENTE,
        )

    def remove_account(self, user_id: str) -> None:
        self._provider.delete_user(user_id)
