from app.core.exceptions import ValidationError
from app.modules.appointment.domain.entities import Appointment
from app.modules.appointment.domain.ports import AuthorizationStore
from app.modules.appointment.domain.validators.base import AppointmentValidator
from app.shared.clock import Clock


class MedicinaGeneralValidator(AppointmentValidator):
    """
    Sin autorización médica vigente para ese servicio, el paciente solo puede agendar Consulta
    General: allí el médico decide si lo remite a un servicio especializado.
    """

    def __init__(self, authorizations: AuthorizationStore, clock: Clock):
        self._authorizations = authorizations
        self._clock = clock

    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        # Al reagendar no se vuelve a exigir: la autorización ya se usó al crear la cita.
        if appointment.appointment_id is not None or not appointment.service_type.requires_authorization:
            return

        authorization = self._authorizations.find_active(appointment.patient_id, self._clock.now())
        if authorization is None or authorization.service_type != appointment.service_type:
            raise ValidationError(
                f"Para agendar {appointment.service_type.label} necesitas una autorización médica "
                "vigente. Agenda una Consulta General para que el médico pueda autorizarte."
            )
