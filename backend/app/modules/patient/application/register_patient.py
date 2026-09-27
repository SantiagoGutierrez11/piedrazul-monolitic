"""Caso de uso: un paciente crea su cuenta para poder agendar citas."""
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from app.core.exceptions import ConflictError, ValidationError
from app.modules.patient.domain.entities import DocumentType, Gender, Patient
from app.modules.patient.infrastructure.repository import PatientRepository

OLDEST_BIRTH_DATE = date(1900, 1, 1)


class AccountRegistrar(Protocol):
    """Contrato que el módulo `identity` expone para crear la cuenta de acceso del paciente."""

    def create_patient_account(self, email: str, password: str, first_name: str, last_name: str) -> str: ...

    def remove_account(self, user_id: str) -> None: ...


@dataclass(frozen=True)
class PatientRegistration:
    first_name: str
    middle_name: str
    last_name: str
    second_last_name: str
    email: str
    phone: str
    birth_date: date
    gender: Gender
    document_type: DocumentType
    document_number: str
    password: str


class RegisterPatient:
    def __init__(self, repository: PatientRepository, accounts: AccountRegistrar):
        self._repository = repository
        self._accounts = accounts

    def execute(self, data: PatientRegistration) -> Patient:
        email = data.email.strip().lower()
        self._validate(data, email)

        user_id = self._accounts.create_patient_account(
            email=email,
            password=data.password,
            first_name=_join(data.first_name, data.middle_name),
            last_name=_join(data.last_name, data.second_last_name),
        )
        patient = Patient(
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            second_last_name=data.second_last_name,
            phone=data.phone,
            email=email,
            birth_date=data.birth_date,
            gender=data.gender,
            document_type=data.document_type,
            document_number=data.document_number,
            user_id=user_id,
        )
        try:
            return self._repository.save(patient)
        except Exception:
            # Sin paciente no debe quedar una cuenta huérfana en el proveedor de identidad.
            self._accounts.remove_account(user_id)
            raise

    def _validate(self, data: PatientRegistration, email: str) -> None:
        if data.birth_date > date.today():
            raise ValidationError("La fecha de nacimiento no puede ser posterior a hoy")
        if data.birth_date < OLDEST_BIRTH_DATE:
            raise ValidationError("La fecha de nacimiento no es válida")
        if self._repository.find_by_email(email):
            raise ConflictError("Ya existe una cuenta registrada con ese correo electrónico")
        if self._repository.find_by_document(data.document_type, data.document_number):
            raise ConflictError("Ya existe un paciente registrado con ese documento")


def _join(*parts: str) -> str:
    return " ".join(part for part in parts if part)
