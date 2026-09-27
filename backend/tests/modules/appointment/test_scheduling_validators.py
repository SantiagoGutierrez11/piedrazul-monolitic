"""Pruebas unitarias de cada eslabón de la cadena de validación del agendamiento."""
from dataclasses import dataclass
from datetime import date, datetime, time

import pytest

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.modules.appointment.domain.entities import (
    Appointment,
    AppointmentStatus,
    PatientAuthorization,
    ServiceType,
)
from app.modules.appointment.domain.validators.active_appointment_validator import (
    ActiveAppointmentValidator,
)
from app.modules.appointment.domain.validators.conflict_validator import ConflictValidator
from app.modules.appointment.domain.validators.data_appointment_validator import (
    DataAppointmentValidator,
)
from app.modules.appointment.domain.validators.existence_validator import ExistenceValidator
from app.modules.appointment.domain.validators.holiday_validator import HolidayValidator
from app.modules.appointment.domain.validators.medicina_general_validator import (
    MedicinaGeneralValidator,
)
from app.modules.appointment.domain.validators.service_offered_validator import (
    ServiceOfferedValidator,
)
from app.modules.appointment.domain.validators.window_validator import AppointmentWindowValidator
from app.modules.appointment.domain.validators.working_hours_validator import (
    WorkingHoursValidator,
)
from app.shared.holidays import ColombianHolidays
from tests.conftest import MONDAY_MORNING, FixedClock

TUESDAY = date(2026, 3, 10)


def _appointment(**overrides) -> Appointment:
    data = dict(
        patient_id=1,
        doctor_id=1,
        doctor_name="Dra. Laura Muñoz",
        service_type=ServiceType.CONSULTA_GENERAL,
        date=TUESDAY,
        start_time=time(9, 0),
        end_time=time(9, 30),
        reason="Control general",
    )
    data.update(overrides)
    return Appointment(**data)


@dataclass
class Doctor:
    full_name: str = "Dra. Laura Muñoz"
    specialty: str = "Medicina General"
    active: bool = True


class Doctors:
    def __init__(self, doctor: Doctor | None = Doctor()):
        self._doctor = doctor

    def find(self, doctor_id):
        return self._doctor


class Patients:
    def __init__(self, exists=True):
        self._exists = exists

    def exists(self, patient_id):
        return self._exists

    def find_id_by_user(self, user_id):
        return 1


@dataclass
class Hours:
    start_time: time = time(8, 0)
    end_time: time = time(12, 0)
    interval_minutes: int = 30


class Schedules:
    def __init__(self, hours: Hours | None = Hours(), weeks=4):
        self._hours, self._weeks = hours, weeks

    def appointment_window_weeks(self):
        return self._weeks

    def working_hours_on(self, doctor_id, on_date):
        return self._hours


class Authorizations:
    def __init__(self, authorization=None):
        self._authorization = authorization

    def find_active(self, patient_id, now):
        return self._authorization

    def save(self, authorization):
        return authorization


class ActiveAppointments:
    def __init__(self, active=()):
        self._active = list(active)

    def find_active_by_patient(self, patient_id, from_date):
        return self._active


CLOCK = FixedClock(MONDAY_MORNING)


# ---------------------------------------------------------------- Datos básicos


def test_data_validator_rejects_past_time():
    with pytest.raises(ValidationError, match="pasada"):
        DataAppointmentValidator(CLOCK).validate(_appointment(date=date(2026, 3, 9), start_time=time(6, 30)), [])


def test_data_validator_rejects_short_reason():
    with pytest.raises(ValidationError, match="motivo"):
        DataAppointmentValidator(CLOCK).validate(_appointment(reason="ok"), [])


# ---------------------------------------------------------------- Festivos


def test_holiday_validator_rejects_colombian_holiday():
    with pytest.raises(ValidationError, match="festivos"):
        HolidayValidator(ColombianHolidays()).validate(_appointment(date=date(2026, 3, 23)), [])


# ---------------------------------------------------------------- Existencia y servicio


def test_existence_validator_rejects_unknown_doctor():
    with pytest.raises(NotFoundError):
        ExistenceValidator(Doctors(None), Patients()).validate(_appointment(), [])


def test_existence_validator_rejects_inactive_doctor():
    with pytest.raises(ValidationError, match="no está atendiendo"):
        ExistenceValidator(Doctors(Doctor(active=False)), Patients()).validate(_appointment(), [])


def test_existence_validator_rejects_unknown_patient():
    with pytest.raises(NotFoundError):
        ExistenceValidator(Doctors(), Patients(exists=False)).validate(_appointment(), [])


def test_service_validator_rejects_professional_of_another_specialty():
    appointment = _appointment(service_type=ServiceType.QUIROPRAXIA)

    with pytest.raises(ValidationError, match="no presta el servicio de Quiropraxia"):
        ServiceOfferedValidator(Doctors()).validate(appointment, [])


# ---------------------------------------------------------------- Cita activa y ventana


def test_active_validator_allows_only_one_active_appointment():
    validator = ActiveAppointmentValidator(ActiveAppointments([_appointment(appointment_id=3)]), CLOCK)

    with pytest.raises(ConflictError, match="Ya tienes una cita agendada"):
        validator.validate(_appointment(), [])


def test_active_validator_does_not_apply_when_rescheduling():
    validator = ActiveAppointmentValidator(ActiveAppointments([_appointment(appointment_id=3)]), CLOCK)

    validator.validate(_appointment(appointment_id=3), [])


def test_window_validator_rejects_dates_beyond_the_configured_weeks():
    validator = AppointmentWindowValidator(Schedules(weeks=2), CLOCK)

    validator.validate(_appointment(date=date(2026, 3, 23)), [])
    with pytest.raises(ValidationError, match="hasta 2 semana"):
        validator.validate(_appointment(date=date(2026, 3, 24)), [])


# ---------------------------------------------------------------- Horario del profesional


def test_working_hours_validator_rejects_a_day_off():
    with pytest.raises(ValidationError, match="no atiende ese día"):
        WorkingHoursValidator(Schedules(hours=None)).validate(_appointment(), [])


@pytest.mark.parametrize(
    "start, end",
    [(time(7, 30), time(8, 0)), (time(11, 45), time(12, 15)), (time(9, 10), time(9, 40)), (time(9, 0), time(10, 0))],
    ids=["antes-de-abrir", "despues-de-cerrar", "fuera-del-intervalo", "duracion-distinta"],
)
def test_working_hours_validator_rejects_slots_outside_the_schedule(start, end):
    with pytest.raises(ValidationError, match="no atiende en ese horario"):
        WorkingHoursValidator(Schedules()).validate(_appointment(start_time=start, end_time=end), [])


def test_working_hours_validator_accepts_the_last_slot_of_the_day():
    WorkingHoursValidator(Schedules()).validate(_appointment(start_time=time(11, 30), end_time=time(12, 0)), [])


# ---------------------------------------------------------------- Autorización médica


def _authorization(service=ServiceType.FISIOTERAPIA) -> PatientAuthorization:
    return PatientAuthorization.grant(_appointment(appointment_id=5), service, datetime(2026, 3, 2, 9, 0))


def test_specialized_service_requires_authorization():
    validator = MedicinaGeneralValidator(Authorizations(None), CLOCK)

    with pytest.raises(ValidationError, match="autorización médica"):
        validator.validate(_appointment(service_type=ServiceType.FISIOTERAPIA), [])


def test_authorization_for_another_service_is_not_enough():
    validator = MedicinaGeneralValidator(Authorizations(_authorization(ServiceType.QUIROPRAXIA)), CLOCK)

    with pytest.raises(ValidationError):
        validator.validate(_appointment(service_type=ServiceType.FISIOTERAPIA), [])


def test_authorized_specialized_service_is_accepted():
    validator = MedicinaGeneralValidator(Authorizations(_authorization()), CLOCK)

    validator.validate(_appointment(service_type=ServiceType.FISIOTERAPIA), [])


def test_general_consultation_never_requires_authorization():
    MedicinaGeneralValidator(Authorizations(None), CLOCK).validate(_appointment(), [])


# ---------------------------------------------------------------- Conflicto de horario


def test_conflict_validator_lets_a_rescheduled_appointment_keep_its_slot():
    existing = [_appointment(appointment_id=9, status=AppointmentStatus.REAGENDADA)]

    ConflictValidator().validate(_appointment(appointment_id=9), existing)
