from app.modules.appointment.application.scheduling.base import AppointmentSchedulingTemplate
from app.modules.appointment.domain.entities import Appointment
from app.modules.appointment.domain.validators.base import AppointmentValidator
from app.modules.appointment.infrastructure.repository import AppointmentRepository


class AutonomousAppointmentScheduling(AppointmentSchedulingTemplate):
    """Agendamiento autónomo con reglas anti-fraude e inyección de validadores."""

    def __init__(self, repository: AppointmentRepository, validators: list[AppointmentValidator]):
        super().__init__(repository, validators)

    def _assign_status(self, appointment: Appointment) -> None:
        # Transición explícita para agendamiento autónomo
        appointment.schedule()
