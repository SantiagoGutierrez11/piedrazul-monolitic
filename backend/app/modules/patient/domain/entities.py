"""Entidades del módulo de pacientes."""
from dataclasses import dataclass
from datetime import date
from enum import Enum


class Gender(str, Enum):
    FEMENINO = "FEMENINO"
    MASCULINO = "MASCULINO"
    OTRO = "OTRO"


class DocumentType(str, Enum):
    CC = "CC"  # Cédula de ciudadanía
    TI = "TI"  # Tarjeta de identidad
    CE = "CE"  # Cédula de extranjería
    PA = "PA"  # Pasaporte


@dataclass
class Patient:
    first_name: str
    last_name: str
    phone: str
    patient_id: int | None = None
    middle_name: str = ""
    second_last_name: str = ""
    email: str | None = None
    birth_date: date | None = None
    gender: Gender | None = None
    document_type: DocumentType | None = None
    document_number: str | None = None
    # Identificador de la cuenta de acceso en Keycloak; vacío para pacientes sin cuenta.
    user_id: str | None = None

    @property
    def full_name(self) -> str:
        parts = (self.first_name, self.middle_name, self.last_name, self.second_last_name)
        return " ".join(part for part in parts if part)
