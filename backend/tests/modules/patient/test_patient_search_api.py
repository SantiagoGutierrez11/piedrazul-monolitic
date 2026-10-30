"""Búsqueda de pacientes por cédula para el historial de citas (E7-HU1, 3.1)."""
import pytest

from app.core.security import Role
from app.modules.patient.domain.entities import DocumentType, Patient
from app.modules.patient.infrastructure.repository import PatientRepository

URL = "/api/v1/patients/search"


def _patients(db_session) -> None:
    repository = PatientRepository(db_session)
    for patient_id, name, document in [
        (1, "María", "1061234567"),
        (2, "Carlos", "1061234890"),
        (3, "Laura", "1062345678"),
        (4, "Andrés", "94512345"),
        (5, "Pedro", "1061"),  # documento corto: es la coincidencia exacta de "1061"
    ]:
        repository.save(
            Patient(
                patient_id=patient_id,
                first_name=name,
                last_name="Prueba",
                phone="3000000000",
                document_type=DocumentType.CC,
                document_number=document,
            )
        )


def test_suggests_patients_whose_id_number_starts_with_the_typed_digits(client, db_session, login_as):
    _patients(db_session)
    login_as(Role.AGENDADOR)

    body = client.get(URL, params={"document": "106123"}).json()

    assert [(p["fullName"], p["documentNumber"]) for p in body] == [
        ("María Prueba", "1061234567"),
        ("Carlos Prueba", "1061234890"),
    ]
    assert body[0] == {
        "patientId": 1,
        "fullName": "María Prueba",
        "documentType": "CC",
        "documentNumber": "1061234567",
        "phone": "3000000000",
    }


def test_the_exact_match_comes_first(client, db_session, login_as):
    _patients(db_session)
    login_as(Role.MEDICO)

    body = client.get(URL, params={"document": "1061"}).json()

    assert body[0]["documentNumber"] == "1061"


def test_no_suggestions_before_the_third_digit(client, db_session, login_as):
    _patients(db_session)
    login_as(Role.ADMINISTRADOR)

    assert client.get(URL, params={"document": "10"}).json() == []


def test_an_unknown_id_number_returns_an_empty_list(client, db_session, login_as):
    _patients(db_session)
    login_as(Role.AGENDADOR)

    assert client.get(URL, params={"document": "999999"}).json() == []


@pytest.mark.parametrize("document", ["1.061.234", "10612a", "10612345678"])
def test_rejects_an_invalid_id_number(client, login_as, document):
    login_as(Role.AGENDADOR)

    response = client.get(URL, params={"document": document})

    assert response.status_code == 400


def test_patients_cannot_search_other_patients(client, login_as):
    login_as(Role.PACIENTE)

    assert client.get(URL, params={"document": "106123"}).status_code == 403
