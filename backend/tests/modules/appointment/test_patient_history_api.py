"""Historial de citas de un paciente para el personal (E7-HU1, 3.2)."""
from datetime import date, time

import pytest

from app.core.security import Role
from app.modules.appointment.domain.entities import AppointmentStatus
from tests.scheduling_helpers import CARLOS_ID, GENERAL, MARIA_ID, PHYSIO, book, create_clinic


def _url(patient_id: int) -> str:
    return f"/api/v1/appointments/patient/{patient_id}/history"


@pytest.mark.parametrize("role", [Role.MEDICO, Role.AGENDADOR, Role.ADMINISTRADOR])
def test_staff_see_the_whole_history_from_the_newest_appointment(client, db_session, login_as, role):
    create_clinic(db_session)
    book(db_session, MARIA_ID, GENERAL, date(2026, 3, 9), time(8, 0), status=AppointmentStatus.ATENDIDA)
    book(db_session, MARIA_ID, PHYSIO, date(2026, 4, 14), time(9, 0))
    book(db_session, MARIA_ID, GENERAL, date(2026, 3, 9), time(11, 0), status=AppointmentStatus.CANCELADA)
    book(db_session, CARLOS_ID, GENERAL, date(2026, 3, 10), time(8, 0))
    login_as(role)

    body = client.get(_url(MARIA_ID)).json()

    assert [(item["date"], item["startTime"], item["status"]) for item in body] == [
        ("2026-04-14", "09:00:00", "AGENDADA"),
        ("2026-03-09", "11:00:00", "CANCELADA"),
        ("2026-03-09", "08:00:00", "ATENDIDA"),
    ]
    assert {item["patientId"] for item in body} == {MARIA_ID}


def test_a_registered_patient_without_appointments_has_an_empty_history(client, db_session, login_as):
    create_clinic(db_session)
    login_as(Role.AGENDADOR)

    response = client.get(_url(CARLOS_ID))

    assert response.status_code == 200
    assert response.json() == []


def test_an_unknown_patient_is_not_found(client, db_session, login_as):
    create_clinic(db_session)
    login_as(Role.MEDICO)

    response = client.get(_url(999))

    assert response.status_code == 404
    assert response.json()["message"] == "El paciente no existe"


def test_a_patient_cannot_see_the_history_of_another_patient(client, db_session, login_as):
    create_clinic(db_session)
    book(db_session, CARLOS_ID, GENERAL, date(2026, 3, 10), time(8, 0))
    login_as(Role.PACIENTE)

    assert client.get(_url(CARLOS_ID)).status_code == 403
