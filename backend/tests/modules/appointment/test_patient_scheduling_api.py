"""Pruebas de extremo a extremo del agendamiento autónomo del paciente."""
from datetime import date, datetime, time

import pytest

from app.core.security import Role
from app.modules.appointment.domain.entities import AppointmentStatus, ServiceType
from app.modules.appointment.infrastructure.authorization_repository import AuthorizationRepository
from tests.conftest import MONDAY_MORNING
from tests.scheduling_helpers import (
    CARLOS_ID,
    CARLOS_USER,
    CHIRO,
    GENERAL,
    MARIA_ID,
    MARIA_USER,
    PHYSIO,
    authorize,
    book,
    create_clinic,
)

URL = "/api/v1/appointments/autonomous"
TUESDAY = "2026-03-10"


@pytest.fixture()
def maria(client, db_session, clock, login_as):
    create_clinic(db_session)
    login_as(Role.PACIENTE, user_id=MARIA_USER)
    return client


def _booking(**overrides) -> dict:
    data = {"doctorId": GENERAL, "serviceType": "CONSULTA_GENERAL", "date": TUESDAY, "startTime": "09:00"}
    data.update(overrides)
    return data


# ---------------------------------------------------------------- Opciones de agendamiento


def test_new_patient_can_only_book_general_consultation(maria):
    body = maria.get("/api/v1/appointments/me/options").json()

    allowed = {service["serviceType"]: service["allowed"] for service in body["services"]}
    assert allowed == {"CONSULTA_GENERAL": True, "FISIOTERAPIA": False, "QUIROPRAXIA": False, "TERAPIA_NEURAL": False}
    assert body["services"][1]["specialty"] == "Fisioterapia"
    assert body["services"][1]["lockedReason"] == "Requiere autorización médica de una Consulta General"
    assert body["authorization"] is None
    assert body["activeAppointment"] is None
    assert body["lastBookableDate"] == "2026-04-06"


def test_authorization_enables_the_authorized_service(maria, db_session):
    authorize(db_session, MARIA_ID, ServiceType.FISIOTERAPIA)

    body = maria.get("/api/v1/appointments/me/options").json()

    allowed = [service["serviceType"] for service in body["services"] if service["allowed"]]
    assert allowed == ["CONSULTA_GENERAL", "FISIOTERAPIA"]
    assert body["authorization"]["label"] == "Fisioterapia"


# ---------------------------------------------------------------- Agendar


def test_patient_books_a_general_consultation(maria):
    response = maria.post(URL, json=_booking(reason="Dolor de cabeza frecuente"))

    assert response.status_code == 201
    body = response.json()
    assert body["patientId"] == MARIA_ID
    assert body["doctorName"] == "Dra. Laura Muñoz"
    assert (body["startTime"], body["endTime"]) == ("09:00:00", "09:30:00")
    assert body["status"] == "AGENDADA"
    assert body["reason"] == "Dolor de cabeza frecuente"


def test_patient_always_books_for_herself(maria):
    body = maria.post(URL, json={**_booking(), "patientId": CARLOS_ID}).json()

    assert body["patientId"] == MARIA_ID


def test_only_one_active_appointment_per_patient(maria):
    maria.post(URL, json=_booking())

    response = maria.post(URL, json=_booking(startTime="10:00"))

    assert response.status_code == 409
    assert response.json()["message"].startswith("Ya tienes una cita agendada")


def test_slot_taken_by_another_patient_is_rejected(maria, db_session):
    book(db_session, CARLOS_ID, GENERAL, date(2026, 3, 10), time(9, 0))

    response = maria.post(URL, json=_booking())

    assert response.status_code == 409
    assert response.json() == {"message": "Ese horario ya no está disponible. Por favor elige otro."}


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"date": "2026-03-23"}, "festivos"),
        ({"date": "2026-04-07"}, "hasta 4 semana"),
        ({"date": "2026-03-14"}, "no atiende ese día"),
        ({"startTime": "07:30"}, "no atiende en ese horario"),
        ({"startTime": "09:15"}, "no atiende en ese horario"),
        ({"doctorId": PHYSIO}, "no presta el servicio de Consulta General"),
        ({"reason": "mal"}, "motivo"),
    ],
    ids=["festivo", "fuera-de-ventana", "sabado", "antes-de-abrir", "fuera-de-intervalo", "otra-especialidad", "motivo-corto"],
)
def test_booking_rules(maria, overrides, message):
    response = maria.post(URL, json=_booking(**overrides))

    assert response.status_code == 400
    assert message in response.json()["message"]


def test_specialized_service_without_authorization_is_rejected(maria):
    response = maria.post(URL, json=_booking(doctorId=PHYSIO, serviceType="FISIOTERAPIA"))

    assert response.status_code == 400
    assert "autorización médica" in response.json()["message"]


def test_booking_a_specialized_service_uses_up_the_authorization(maria, db_session):
    authorize(db_session, MARIA_ID, ServiceType.FISIOTERAPIA)

    response = maria.post(URL, json=_booking(doctorId=PHYSIO, serviceType="FISIOTERAPIA"))

    assert response.status_code == 201
    assert AuthorizationRepository(db_session).find_active(MARIA_ID, MONDAY_MORNING) is None


def test_professional_without_schedule_cannot_be_booked(maria, db_session):
    authorize(db_session, MARIA_ID, ServiceType.QUIROPRAXIA)

    response = maria.post(URL, json=_booking(doctorId=CHIRO, serviceType="QUIROPRAXIA"))

    assert response.status_code == 400


def test_staff_cannot_book_as_a_patient(client, db_session, clock, login_as):
    create_clinic(db_session)
    login_as(Role.AGENDADOR)

    assert client.post(URL, json=_booking()).status_code == 403


def test_patient_account_without_profile_gets_not_found(client, db_session, clock, login_as):
    create_clinic(db_session)
    login_as(Role.PACIENTE, user_id="kc-sin-perfil")

    assert client.post(URL, json=_booking()).status_code == 404


# ---------------------------------------------------------------- Mis citas y cancelación


def test_patient_lists_only_her_appointments(maria, db_session):
    book(db_session, CARLOS_ID, GENERAL, date(2026, 3, 11), time(8, 0))
    maria.post(URL, json=_booking())

    body = maria.get("/api/v1/appointments/me").json()

    assert [item["patientId"] for item in body] == [MARIA_ID]


def test_cancelling_frees_the_patient_to_book_again(maria):
    appointment_id = maria.post(URL, json=_booking()).json()["appointmentId"]

    cancelled = maria.patch(f"/api/v1/appointments/me/{appointment_id}/cancel")
    rebooked = maria.post(URL, json=_booking(startTime="10:30"))

    assert cancelled.json()["status"] == "CANCELADA"
    assert rebooked.status_code == 201


def test_patient_cannot_cancel_someone_elses_appointment(maria, db_session):
    other = book(db_session, CARLOS_ID, GENERAL, date(2026, 3, 11), time(8, 0))

    response = maria.patch(f"/api/v1/appointments/me/{other.appointment_id}/cancel")

    assert response.status_code == 404


# ---------------------------------------------------------------- Atención del médico


def test_doctor_attending_can_authorize_a_specialized_service(client, db_session, clock, login_as):
    create_clinic(db_session)
    appointment = book(db_session, CARLOS_ID, GENERAL, date(2026, 3, 9), time(9, 0))
    login_as(Role.MEDICO)

    response = client.patch(
        f"/api/v1/appointments/{appointment.appointment_id}/attend",
        json={"authorizedServiceType": "TERAPIA_NEURAL"},
    )

    assert response.json()["status"] == AppointmentStatus.ATENDIDA.value
    authorization = AuthorizationRepository(db_session).find_active(CARLOS_ID, MONDAY_MORNING)
    assert authorization.service_type == ServiceType.TERAPIA_NEURAL
    assert authorization.expires_at == datetime(2026, 4, 9, 7, 0)
    login_as(Role.PACIENTE, user_id=CARLOS_USER)
    options = client.get("/api/v1/appointments/me/options").json()
    assert [s["serviceType"] for s in options["services"] if s["allowed"]] == ["CONSULTA_GENERAL", "TERAPIA_NEURAL"]
