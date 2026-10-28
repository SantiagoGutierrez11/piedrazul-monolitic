"""Orden del historial y roles que lo consultan (E7-HU1, 2.2 y 2.3)."""
from datetime import date, time

import pytest

from app.core.exceptions import ForbiddenError
from app.core.security import CurrentUser, Role
from app.modules.appointment.application.list_appointments import AppointmentWithPatient
from app.modules.appointment.application.patient_history import ensure_can_consult, newest_first
from app.modules.appointment.domain.entities import Appointment, AppointmentStatus, ServiceType


def _item(on_date: date, start: time, status=AppointmentStatus.ATENDIDA) -> AppointmentWithPatient:
    appointment = Appointment(
        patient_id=1,
        doctor_id=1,
        doctor_name="Dra. Laura Muñoz",
        service_type=ServiceType.CONSULTA_GENERAL,
        date=on_date,
        start_time=start,
        end_time=time(start.hour, 30),
        reason="",
        status=status,
    )
    return AppointmentWithPatient(appointment=appointment, patient=None)


def _user(*roles: Role) -> CurrentUser:
    return CurrentUser(user_id="u1", email="x@piedrazul.com", full_name="Usuario", roles=frozenset(roles))


def test_history_goes_from_the_newest_to_the_oldest_appointment():
    listing = [
        _item(date(2026, 9, 10), time(9, 0)),
        _item(date(2026, 11, 3), time(10, 0), AppointmentStatus.AGENDADA),
        _item(date(2026, 9, 10), time(11, 0), AppointmentStatus.CANCELADA),
    ]

    ordered = newest_first(listing)

    assert [(i.appointment.date, i.appointment.start_time) for i in ordered] == [
        (date(2026, 11, 3), time(10, 0)),
        (date(2026, 9, 10), time(11, 0)),
        (date(2026, 9, 10), time(9, 0)),
    ]


@pytest.mark.parametrize("role", [Role.MEDICO, Role.AGENDADOR, Role.ADMINISTRADOR])
def test_staff_can_consult_the_history(role):
    ensure_can_consult(_user(role))


def test_a_patient_cannot_consult_the_history_of_others():
    with pytest.raises(ForbiddenError):
        ensure_can_consult(_user(Role.PACIENTE))
