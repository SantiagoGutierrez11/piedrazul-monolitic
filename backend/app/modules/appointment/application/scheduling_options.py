"""Qué puede agendar el paciente en este momento: servicios habilitados, autorización y cita activa."""
from dataclasses import dataclass
from datetime import date, timedelta

from app.core.exceptions import NotFoundError
from app.modules.appointment.domain.entities import Appointment, PatientAuthorization, ServiceType
from app.modules.appointment.domain.ports import (
    AuthorizationStore,
    PatientAppointments,
    PatientLookup,
    ScheduleLookup,
)
from app.shared.clock import Clock

LOCKED_REASON = "Requiere autorización médica de una Consulta General"


@dataclass(frozen=True)
class ServiceOption:
    service_type: ServiceType
    allowed: bool
    locked_reason: str | None


@dataclass(frozen=True)
class SchedulingOptions:
    services: list[ServiceOption]
    authorization: PatientAuthorization | None
    active_appointment: Appointment | None
    window_weeks: int
    last_bookable_date: date


class SchedulingOptionsQuery:
    def __init__(
        self,
        appointments: PatientAppointments,
        patients: PatientLookup,
        schedules: ScheduleLookup,
        authorizations: AuthorizationStore,
        clock: Clock,
    ):
        self._appointments = appointments
        self._patients = patients
        self._schedules = schedules
        self._authorizations = authorizations
        self._clock = clock

    def for_user(self, user_id: str) -> SchedulingOptions:
        patient_id = self._patients.find_id_by_user(user_id)
        if patient_id is None:
            raise NotFoundError("No se encontró el perfil del paciente")

        now = self._clock.now()
        authorization = self._authorizations.find_active(patient_id, now)
        active = self._appointments.find_active_by_patient(patient_id, now.date())
        weeks = self._schedules.appointment_window_weeks()

        return SchedulingOptions(
            services=[self._option(service, authorization) for service in ServiceType],
            authorization=authorization,
            active_appointment=active[0] if active else None,
            window_weeks=weeks,
            last_bookable_date=now.date() + timedelta(weeks=weeks),
        )

    @staticmethod
    def _option(service: ServiceType, authorization: PatientAuthorization | None) -> ServiceOption:
        allowed = not service.requires_authorization or (
            authorization is not None and authorization.service_type == service
        )
        return ServiceOption(service_type=service, allowed=allowed, locked_reason=None if allowed else LOCKED_REASON)
