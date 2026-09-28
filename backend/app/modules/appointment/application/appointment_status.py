"""Cambios de estado de una cita ya agendada: cancelación (paciente o personal) y atención por el médico."""
from app.core.event_bus import publish
from app.core.exceptions import NotFoundError
from app.modules.appointment.domain.entities import Appointment, PatientAuthorization, ServiceType
from app.modules.appointment.domain.ports import AuthorizationStore, PatientLookup
from app.modules.appointment.infrastructure.repository import AppointmentRepository
from app.shared.clock import Clock


class CancelPatientAppointment:
    def __init__(self, repository: AppointmentRepository, patients: PatientLookup):
        self._repository = repository
        self._patients = patients

    def execute(self, user_id: str, appointment_id: int) -> Appointment:
        appointment = self._repository.find_by_id(appointment_id)
        # Una cita ajena se reporta como inexistente para no revelar citas de otros pacientes.
        if appointment is None or appointment.patient_id != self._patients.find_id_by_user(user_id):
            raise NotFoundError("No se encontró la cita")

        appointment.cancel()
        saved = self._repository.save(appointment)
        publish("appointment.cancelled", {"appointment_id": saved.appointment_id})
        return saved


class CancelAppointment:
    """El personal del centro cancela una cita a nombre del paciente."""

    def __init__(self, repository: AppointmentRepository):
        self._repository = repository

    def execute(self, appointment_id: int) -> Appointment:
        appointment = self._repository.find_by_id(appointment_id)
        if appointment is None:
            raise NotFoundError("No se encontró la cita")

        appointment.cancel()
        saved = self._repository.save(appointment)
        publish("appointment.cancelled", {"appointment_id": saved.appointment_id})
        return saved


class AttendAppointment:
    """El médico marca la cita como atendida y, si corresponde, autoriza un servicio especializado."""

    def __init__(self, repository: AppointmentRepository, authorizations: AuthorizationStore, clock: Clock):
        self._repository = repository
        self._authorizations = authorizations
        self._clock = clock

    def execute(self, appointment_id: int, authorized_service: ServiceType | None = None) -> Appointment:
        appointment = self._repository.find_by_id(appointment_id)
        if appointment is None:
            raise NotFoundError("No se encontró la cita")

        now = self._clock.now()
        appointment.mark_as_attended(now.date())
        saved = self._repository.save(appointment)

        if authorized_service is not None:
            self._authorizations.save(PatientAuthorization.grant(saved, authorized_service, now))

        publish("appointment.attended", {"appointment_id": saved.appointment_id})
        return saved
