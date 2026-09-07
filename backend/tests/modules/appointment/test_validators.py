"""Ejemplo de test unitario de dominio (equivalente a ConflictAppointmentValidatorTest.java)."""
from datetime import date, time

import pytest

from app.core.exceptions import ConflictError
from app.modules.appointment.domain.entities import Appointment, AppointmentStatus, ServiceType
from app.modules.appointment.domain.validators.conflict_validator import ConflictValidator


def _appointment(start: time, status: AppointmentStatus = AppointmentStatus.AGENDADA) -> Appointment:
    return Appointment(
        patient_id=1,
        doctor_id=1,
        doctor_name="Dra. Test",
        service_type=ServiceType.CONSULTA_GENERAL,
        date=date(2026, 3, 10),
        start_time=start,
        end_time=start,
        reason="control",
        status=status,
    )


def test_conflict_validator_rejects_same_slot():
    validator = ConflictValidator()
    existing = [_appointment(time(9, 0))]

    with pytest.raises(ConflictError):
        validator.validate(_appointment(time(9, 0)), existing)


def test_conflict_validator_ignores_cancelled():
    validator = ConflictValidator()
    existing = [_appointment(time(9, 0), status=AppointmentStatus.CANCELADA)]

    validator.validate(_appointment(time(9, 0)), existing)  # no debe lanzar
