"""Entidades del módulo de pacientes."""
from dataclasses import dataclass


@dataclass
class Patient:
    patient_id: int
    first_name: str
    last_name: str
    phone: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
