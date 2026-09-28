"""Consultas y acciones que alimentan los paneles del médico, el agendador y el administrador."""
from datetime import date, time

from app.core.security import Role
from app.modules.appointment.domain.entities import AppointmentStatus
from app.modules.medical_staff.domain.entities import Doctor
from app.modules.medical_staff.infrastructure.repository import DoctorRepository
from tests.scheduling_helpers import CARLOS_ID, GENERAL, MARIA_ID, PHYSIO, book, create_clinic

MONDAY, TUESDAY = date(2026, 3, 9), date(2026, 3, 10)


def test_staff_lists_every_appointment_of_a_day(client, db_session, clock, login_as):
    create_clinic(db_session)
    book(db_session, MARIA_ID, PHYSIO, MONDAY, time(10, 0))
    book(db_session, CARLOS_ID, GENERAL, MONDAY, time(8, 0))
    book(db_session, CARLOS_ID, GENERAL, TUESDAY, time(8, 0))
    login_as(Role.AGENDADOR)

    body = client.get("/api/v1/appointments/date/2026-03-09").json()
    only_general = client.get("/api/v1/appointments/date/2026-03-09", params={"doctor_id": GENERAL}).json()

    assert [(item["startTime"], item["patientName"]) for item in body] == [
        ("08:00:00", "Carlos Rodríguez"),
        ("10:00:00", "María García"),
    ]
    assert len(only_general) == 1


def test_patients_cannot_see_the_daily_agenda(client, login_as):
    login_as(Role.PACIENTE)

    assert client.get("/api/v1/appointments/date/2026-03-09").status_code == 403


def test_scheduler_cancels_an_appointment(client, db_session, clock, login_as):
    create_clinic(db_session)
    appointment = book(db_session, MARIA_ID, GENERAL, TUESDAY, time(9, 0))
    login_as(Role.AGENDADOR)

    response = client.patch(f"/api/v1/appointments/{appointment.appointment_id}/cancel")

    assert response.json()["status"] == AppointmentStatus.CANCELADA.value
    login_as(Role.MEDICO)
    assert client.patch(f"/api/v1/appointments/{appointment.appointment_id}/cancel").status_code == 403


def test_summary_counts_today_pending_and_the_week(client, db_session, clock, login_as):
    create_clinic(db_session)
    book(db_session, MARIA_ID, GENERAL, MONDAY, time(8, 0))
    book(db_session, CARLOS_ID, GENERAL, MONDAY, time(9, 0), status=AppointmentStatus.CANCELADA)
    book(db_session, CARLOS_ID, PHYSIO, TUESDAY, time(8, 0))
    login_as(Role.ADMINISTRADOR)

    body = client.get("/api/v1/appointments/summary").json()

    assert body["today"] == 1
    assert body["pending"] == 2
    assert [day["count"] for day in body["week"]] == [1, 1, 0, 0, 0, 0, 0]
    assert body["week"][0]["date"] == "2026-03-09"


def test_doctor_gets_the_professional_linked_to_the_account(client, db_session, login_as):
    DoctorRepository(db_session).save(
        Doctor(doctor_id=GENERAL, full_name="Dra. Laura Muñoz", specialty="Medicina General", user_id="kc-laura")
    )
    login_as(Role.MEDICO, user_id="kc-laura")

    assert client.get("/api/v1/medical/doctors/me").json()["fullName"] == "Dra. Laura Muñoz"
    login_as(Role.MEDICO, user_id="kc-otro")
    assert client.get("/api/v1/medical/doctors/me").status_code == 404


def test_admin_counts_registered_patients(client, db_session, login_as):
    create_clinic(db_session)
    login_as(Role.ADMINISTRADOR)

    assert client.get("/api/v1/patients/count").json() == {"total": 2}
