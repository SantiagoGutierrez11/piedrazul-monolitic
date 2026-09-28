"""Entidades del personal médico."""
from dataclasses import dataclass


@dataclass
class Doctor:
    doctor_id: int
    full_name: str
    specialty: str
    active: bool = True
    # Cuenta de Keycloak del profesional; vacía si aún no tiene usuario.
    user_id: str | None = None
