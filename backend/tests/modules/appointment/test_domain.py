"""Pruebas del dominio de citas: invariantes de estado, autorización médica y Builder."""
from datetime import date, datetime, time

import pytest

from app.core.exceptions import ConflictError, ValidationError
from app.modules.appointment.domain.builder.director import (
    PATIENT_DEFAULT_REASON,
    AppointmentDirector,
)
from app.modules.appointment.domain.entities import (
    Appointment,
    AppointmentStatus,
    PatientAuthorization,
    ServiceType,
)

ON_DATE = date(2026, 3, 10)


def _appointment(status=AppointmentStatus.AGENDADA) -> Appointment:
    return Appointment(
        patient_id=1,
        doctor_id=1,
        doctor_name="Dra. Laura Muñoz",
        service_type=ServiceType.CONSULTA_GENERAL,
        date=ON_DATE,
        start_time=time(9, 0),
        end_time=time(9, 30),
        reason="Control general",
        status=status,
        appointment_id=7,
    )


# ---------------------------------------------------------------- Appointment


def test_cancel_changes_status():
    appointment = _appointment()

    appointment.cancel()

    assert appointment.status == AppointmentStatus.CANCELADA
    assert not appointment.is_active


@pytest.mark.parametrize("status", [AppointmentStatus.CANCELADA, AppointmentStatus.ATENDIDA])
def test_cancelled_or_attended_appointment_cannot_be_cancelled(status):
    with pytest.raises(ConflictError):
        _appointment(status).cancel()


def test_attend_only_on_the_appointment_day():
    with pytest.raises(ValidationError):
        _appointment().mark_as_attended(date(2026, 3, 9))


def test_attend_on_the_appointment_day():
    appointment = _appointment()

    appointment.mark_as_attended(ON_DATE)

    assert appointment.status == AppointmentStatus.ATENDIDA


def test_cancelled_appointment_cannot_be_attended():
    with pytest.raises(ConflictError):
        _appointment(AppointmentStatus.CANCELADA).mark_as_attended(ON_DATE)


# ---------------------------------------------------------------- Autorización


def test_authorization_lasts_one_month_and_is_single_use():
    granted_at = datetime(2026, 1, 31, 10, 0)
    authorization = PatientAuthorization.grant(_appointment(), ServiceType.FISIOTERAPIA, granted_at)

    assert authorization.expires_at == datetime(2026, 2, 28, 10, 0)
    assert authorization.is_active(datetime(2026, 2, 27, 10, 0))
    assert not authorization.is_active(datetime(2026, 2, 28, 10, 0))

    authorization.mark_used()
    assert not authorization.is_active(datetime(2026, 2, 1, 10, 0))


def test_general_consultation_does_not_need_authorization():
    with pytest.raises(ValidationError):
        PatientAuthorization.grant(_appointment(), ServiceType.CONSULTA_GENERAL, datetime(2026, 3, 10))


def test_only_general_consultation_is_free_to_book():
    assert [s for s in ServiceType if not s.requires_authorization] == [ServiceType.CONSULTA_GENERAL]


# ---------------------------------------------------------------- Builder y Director


def _slot():
    return dict(on_date=ON_DATE, start_time=time(9, 0), end_time=time(9, 30))


def test_patient_recipe_fills_default_reason_and_marks_it_autonomous():
    appointment = AppointmentDirector().build_patient_appointment(
        patient_id=1, doctor_id=2, doctor_name="Dr. Juan Pérez", service_type=ServiceType.FISIOTERAPIA, **_slot()
    )

    assert appointment.reason == PATIENT_DEFAULT_REASON
    assert appointment.notes == "Agendamiento autónomo"
    assert appointment.service_type == ServiceType.FISIOTERAPIA
    assert appointment.status == AppointmentStatus.AGENDADA
    assert appointment.appointment_id is None


def test_patient_recipe_keeps_the_reason_the_patient_wrote():
    appointment = AppointmentDirector().build_patient_appointment(
        patient_id=1, doctor_id=1, doctor_name="Dra. Laura Muñoz",
        service_type=ServiceType.CONSULTA_GENERAL, reason="  Dolor de espalda  ", **_slot()
    )

    assert appointment.reason == "Dolor de espalda"


def test_manual_recipe_keeps_the_scheduler_notes():
    appointment = AppointmentDirector().build_manual_appointment(
        patient_id=1, doctor_id=1, doctor_name="Dra. Laura Muñoz",
        service_type=ServiceType.CONSULTA_GENERAL, notes="Llamó por teléfono", **_slot()
    )

    assert appointment.reason == "Sin especificar"
    assert appointment.notes == "Llamó por teléfono"
