"""Reporte de próximas citas por semana para el médico, el agendador y el administrador."""
from datetime import date, datetime, time

from app.core.security import Role
from app.modules.appointment.domain.entities import AppointmentStatus
from app.modules.medical_staff.domain.entities import Doctor
from app.modules.medical_staff.infrastructure.repository import DoctorRepository
from tests.scheduling_helpers import CARLOS_ID, GENERAL, MARIA_ID, PHYSIO, book, create_clinic

URL = "/api/v1/appointments/upcoming"
# El reloj de pruebas está en el lunes 9 de marzo de 2026.
MONDAY, THURSDAY, NEXT_TUESDAY = date(2026, 3, 9), date(2026, 3, 12), date(2026, 3, 17)


def _link_doctor_account(db_session) -> None:
    DoctorRepository(db_session).save(
        Doctor(doctor_id=GENERAL, full_name="Dra. Laura Muñoz", specialty="Medicina General", user_id="kc-laura")
    )


def test_scheduler_sees_active_appointments_grouped_by_week(client, db_session, clock, login_as):
    create_clinic(db_session)
    book(db_session, CARLOS_ID, PHYSIO, THURSDAY, time(9, 0))
    book(db_session, MARIA_ID, GENERAL, MONDAY, time(8, 0))
    book(db_session, MARIA_ID, GENERAL, MONDAY, time(10, 0), status=AppointmentStatus.CANCELADA)
    book(db_session, MARIA_ID, PHYSIO, NEXT_TUESDAY, time(8, 0))
    login_as(Role.AGENDADOR)

    body = client.get(URL, params={"weeks": 3}).json()

    assert (body["dateFrom"], body["dateTo"], body["total"]) == ("2026-03-09", "2026-03-29", 3)
    assert [(week["start"], week["end"], week["total"]) for week in body["weeks"]] == [
        ("2026-03-09", "2026-03-15", 2),
        ("2026-03-16", "2026-03-22", 1),
        ("2026-03-23", "2026-03-29", 0),
    ]
    first_week = body["weeks"][0]["appointments"]
    assert [(item["date"], item["startTime"], item["patientName"]) for item in first_week] == [
        ("2026-03-09", "08:00:00", "María García"),
        ("2026-03-12", "09:00:00", "Carlos Rodríguez"),
    ]


def test_days_already_past_this_week_are_left_out(client, db_session, clock, login_as):
    create_clinic(db_session)
    book(db_session, MARIA_ID, GENERAL, MONDAY, time(8, 0))
    book(db_session, CARLOS_ID, GENERAL, THURSDAY, time(8, 0))
    clock.set(datetime(2026, 3, 11, 7, 0))  # miércoles
    login_as(Role.ADMINISTRADOR)

    body = client.get(URL, params={"weeks": 1}).json()

    assert body["dateFrom"] == "2026-03-11"
    assert body["weeks"][0]["start"] == "2026-03-09"
    assert [item["date"] for item in body["weeks"][0]["appointments"]] == ["2026-03-12"]


def test_scheduler_can_filter_by_professional(client, db_session, clock, login_as):
    create_clinic(db_session)
    book(db_session, MARIA_ID, GENERAL, MONDAY, time(8, 0))
    book(db_session, CARLOS_ID, PHYSIO, MONDAY, time(9, 0))
    login_as(Role.AGENDADOR)

    body = client.get(URL, params={"doctor_id": PHYSIO}).json()

    assert body["total"] == 1
    assert body["weeks"][0]["appointments"][0]["doctorId"] == PHYSIO
    assert len(body["weeks"]) == 4  # semanas por defecto


def test_doctor_only_sees_their_own_appointments(client, db_session, clock, login_as):
    create_clinic(db_session)
    _link_doctor_account(db_session)
    book(db_session, MARIA_ID, GENERAL, MONDAY, time(8, 0))
    book(db_session, CARLOS_ID, PHYSIO, MONDAY, time(9, 0))
    login_as(Role.MEDICO, user_id="kc-laura")

    body = client.get(URL).json()

    assert body["total"] == 1
    assert body["weeks"][0]["appointments"][0]["doctorId"] == GENERAL
    assert client.get(URL, params={"doctor_id": PHYSIO}).status_code == 403


def test_doctor_without_a_professional_profile_gets_not_found(client, db_session, clock, login_as):
    create_clinic(db_session)
    login_as(Role.MEDICO, user_id="kc-sin-perfil")

    assert client.get(URL).status_code == 404


def test_patients_cannot_see_the_report(client, clock, login_as):
    login_as(Role.PACIENTE)

    assert client.get(URL).status_code == 403


def test_the_number_of_weeks_is_limited(client, clock, login_as):
    login_as(Role.AGENDADOR)

    assert client.get(URL, params={"weeks": 0}).status_code == 422
    assert client.get(URL, params={"weeks": 9}).status_code == 422
