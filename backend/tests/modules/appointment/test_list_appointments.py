"""Pruebas del listado de citas por médico/fecha y por paciente."""
from datetime import date, time

import pytest

from app.modules.appointment.domain.entities import Appointment, AppointmentStatus, ServiceType
from app.modules.appointment.infrastructure.repository import AppointmentRepository
from app.modules.patient.domain.entities import Patient
from app.modules.patient.infrastructure.repository import PatientRepository

ON_DATE = date(2026, 3, 10)


def _appointment(start: time, **overrides) -> Appointment:
    data = dict(
        patient_id=101,
        doctor_id=1,
        doctor_name="Dra. Test",
        service_type=ServiceType.CONSULTA_GENERAL,
        date=ON_DATE,
        start_time=start,
        end_time=start,
        reason="control",
        status=AppointmentStatus.AGENDADA,
    )
    data.update(overrides)
    return Appointment(**data)


@pytest.fixture()
def repository(db_session):
    return AppointmentRepository(db_session)


@pytest.fixture()
def patients(db_session):
    return PatientRepository(db_session)


def test_list_returns_empty_when_no_appointments(client):
    response = client.get(f"/api/v1/appointments/doctor/1/date/{ON_DATE}")

    assert response.status_code == 200
    assert response.json() == []


def test_list_returns_appointments_ordered_by_start_time(client, repository):
    repository.save(_appointment(time(10, 0)))
    repository.save(_appointment(time(8, 0)))

    body = client.get(f"/api/v1/appointments/doctor/1/date/{ON_DATE}").json()

    assert [item["startTime"] for item in body] == ["08:00:00", "10:00:00"]
    assert body[0]["doctorName"] == "Dra. Test"
    assert body[0]["status"] == "AGENDADA"


def test_list_excludes_other_doctors_and_dates(client, repository):
    repository.save(_appointment(time(8, 0)))
    repository.save(_appointment(time(9, 0), doctor_id=2))
    repository.save(_appointment(time(11, 0), date=date(2026, 3, 11)))

    body = client.get(f"/api/v1/appointments/doctor/1/date/{ON_DATE}").json()

    assert len(body) == 1


def test_list_can_be_filtered_by_status(client, repository):
    repository.save(_appointment(time(8, 0)))
    repository.save(_appointment(time(9, 0), status=AppointmentStatus.CANCELADA))

    body = client.get(
        f"/api/v1/appointments/doctor/1/date/{ON_DATE}", params={"status": "CANCELADA"}
    ).json()

    assert [item["startTime"] for item in body] == ["09:00:00"]


def test_list_by_patient(client, repository):
    repository.save(_appointment(time(8, 0)))
    repository.save(_appointment(time(9, 0), patient_id=999))

    body = client.get("/api/v1/appointments/patient/101").json()

    assert len(body) == 1
    assert body[0]["patientId"] == 101


def test_list_includes_patient_name_and_phone(client, repository, patients):
    patients.save(
        Patient(patient_id=101, first_name="María", last_name="García", phone="+57 300 123 4567")
    )
    repository.save(_appointment(time(8, 0)))

    body = client.get(f"/api/v1/appointments/doctor/1/date/{ON_DATE}").json()

    assert body[0]["patientName"] == "María García"
    assert body[0]["patientPhone"] == "+57 300 123 4567"


def test_list_leaves_patient_name_empty_when_not_registered(client, repository):
    repository.save(_appointment(time(8, 0)))

    body = client.get(f"/api/v1/appointments/doctor/1/date/{ON_DATE}").json()

    assert body[0]["patientName"] is None
