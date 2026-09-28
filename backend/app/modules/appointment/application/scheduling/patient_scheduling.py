"""Caso de uso del agendamiento autónomo: el paciente elige servicio, profesional y franja."""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from app.core.exceptions import NotFoundError
from app.modules.appointment.application.scheduling.autonomous_scheduling import (
    AutonomousAppointmentScheduling,
)
from app.modules.appointment.application.scheduling.validation_chain import build_validation_chain
from app.modules.appointment.domain.builder.director import AppointmentDirector
from app.modules.appointment.domain.entities import Appointment, ServiceType
from app.modules.appointment.domain.ports import (
    AuthorizationStore,
    DoctorLookup,
    PatientLookup,
    ScheduleLookup,
)
from app.modules.appointment.infrastructure.repository import AppointmentRepository
from app.shared.clock import Clock
from app.shared.holidays import ColombianHolidays

# Solo se usa para completar la cita cuando el profesional no atiende ese día; en ese caso
# el validador de horario la rechaza de todos modos.
FALLBACK_DURATION_MINUTES = 30


@dataclass(frozen=True)
class PatientBooking:
    doctor_id: int
    service_type: ServiceType
    date: date
    start_time: time
    reason: str = ""


class SchedulePatientAppointment:
    def __init__(
        self,
        repository: AppointmentRepository,
        patients: PatientLookup,
        doctors: DoctorLookup,
        schedules: ScheduleLookup,
        authorizations: AuthorizationStore,
        clock: Clock,
        holidays: ColombianHolidays | None = None,
    ):
        self._repository = repository
        self._patients = patients
        self._doctors = doctors
        self._schedules = schedules
        self._authorizations = authorizations
        self._clock = clock
        self._holidays = holidays or ColombianHolidays()
        self._director = AppointmentDirector()

    def execute(self, user_id: str, booking: PatientBooking) -> Appointment:
        patient_id = self._patients.find_id_by_user(user_id)
        if patient_id is None:
            raise NotFoundError("No se encontró el perfil del paciente")

        doctor = self._doctors.find(booking.doctor_id)
        hours = self._schedules.working_hours_on(booking.doctor_id, booking.date)
        duration = hours.interval_minutes if hours else FALLBACK_DURATION_MINUTES

        appointment = self._director.build_patient_appointment(
            patient_id=patient_id,
            doctor_id=booking.doctor_id,
            doctor_name=doctor.full_name if doctor else "",
            service_type=booking.service_type,
            on_date=booking.date,
            start_time=booking.start_time,
            end_time=_plus_minutes(booking.start_time, duration),
            reason=booking.reason,
        )

        scheduling = AutonomousAppointmentScheduling(
            self._repository,
            build_validation_chain(
                appointments=self._repository,
                doctors=self._doctors,
                patients=self._patients,
                schedules=self._schedules,
                authorizations=self._authorizations,
                clock=self._clock,
                holidays=self._holidays,
            ),
        )
        saved = scheduling.execute(appointment)
        self._consume_authorization(saved)
        return saved

    def _consume_authorization(self, appointment: Appointment) -> None:
        """La autorización médica se usa una sola vez: queda consumida con la cita especializada."""
        if not appointment.service_type.requires_authorization:
            return
        authorization = self._authorizations.find_active(appointment.patient_id, self._clock.now())
        if authorization is not None:
            authorization.mark_used()
            self._authorizations.save(authorization)


def _plus_minutes(start: time, minutes: int) -> time:
    return (datetime.combine(date.min, start) + timedelta(minutes=minutes)).time()
