"""Pruebas unitarias del caso de uso de registro."""
from datetime import date

import pytest

from app.core.exceptions import ConflictError
from app.modules.patient.application.register_patient import PatientRegistration, RegisterPatient
from app.modules.patient.domain.entities import DocumentType, Gender

REGISTRATION = PatientRegistration(
    first_name="María",
    middle_name="",
    last_name="Gómez",
    second_last_name="",
    email=" Maria.Gomez@Correo.com ",
    phone="3001234567",
    birth_date=date(1958, 4, 12),
    gender=Gender.FEMENINO,
    document_type=DocumentType.CC,
    document_number="1023456789",
    password="clave1234",
)


class RecordingAccounts:
    def __init__(self):
        self.created: list[dict] = []
        self.removed: list[str] = []

    def create_patient_account(self, email, password, first_name, last_name) -> str:
        self.created.append({"email": email, "first_name": first_name, "last_name": last_name})
        return "kc-1"

    def remove_account(self, user_id: str) -> None:
        self.removed.append(user_id)


class RepositoryFailingOnSave:
    def find_by_email(self, email):
        return None

    def find_by_document(self, document_type, document_number):
        return None

    def save(self, patient):
        raise ConflictError("Ya existe un paciente registrado con ese correo o documento")


def test_account_is_removed_when_patient_cannot_be_saved():
    accounts = RecordingAccounts()

    with pytest.raises(ConflictError):
        RegisterPatient(RepositoryFailingOnSave(), accounts).execute(REGISTRATION)

    assert accounts.removed == ["kc-1"]


def test_email_is_normalized_before_creating_the_account():
    accounts = RecordingAccounts()

    with pytest.raises(ConflictError):
        RegisterPatient(RepositoryFailingOnSave(), accounts).execute(REGISTRATION)

    assert accounts.created == [
        {"email": "maria.gomez@correo.com", "first_name": "María", "last_name": "Gómez"}
    ]
