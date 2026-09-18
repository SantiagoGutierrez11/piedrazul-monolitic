"""Pruebas del listado de profesionales usado por los selectores del frontend."""
import pytest

from app.modules.medical_staff.domain.entities import Doctor
from app.modules.medical_staff.infrastructure.repository import DoctorRepository


@pytest.fixture()
def repository(db_session):
    return DoctorRepository(db_session)


def test_list_doctors_returns_empty_when_none(client):
    response = client.get("/api/v1/medical/doctors")

    assert response.status_code == 200
    assert response.json() == []


def test_list_doctors_returns_active_ordered_by_name(client, repository):
    repository.save(Doctor(doctor_id=1, full_name="Dra. Zulma Ríos", specialty="Pediatría"))
    repository.save(Doctor(doctor_id=2, full_name="Dr. Andrés Lima", specialty="Fisioterapia"))

    body = client.get("/api/v1/medical/doctors").json()

    assert [item["fullName"] for item in body] == ["Dr. Andrés Lima", "Dra. Zulma Ríos"]
    assert body[0]["doctorId"] == 2
    assert body[0]["specialty"] == "Fisioterapia"


def test_list_doctors_excludes_inactive(client, repository):
    repository.save(Doctor(doctor_id=1, full_name="Dra. Activa", specialty="General"))
    repository.save(Doctor(doctor_id=2, full_name="Dr. Inactivo", specialty="General", active=False))

    body = client.get("/api/v1/medical/doctors").json()

    assert [item["fullName"] for item in body] == ["Dra. Activa"]
