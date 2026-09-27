from app.core.exceptions import DomainError
from app.modules.appointment.domain.entities import Appointment, AppointmentStatus
from app.modules.appointment.domain.validators.base import AppointmentValidator


class ActiveAppointmentValidator(AppointmentValidator):
    """Regla anti-fraude (RF4): Impide que un paciente tenga más de N citas activas."""

    def __init__(self, max_active_appointments: int = 2):
        self.max_active_appointments = max_active_appointments

    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        # En una consulta real de BD buscaríamos todas las citas activas del paciente.
        # Aquí filtramos las citas en memoria que coincidan con el paciente.
        active_count = sum(
            1 for app in existing_on_date
            if app.patient_id == appointment.patient_id and app.status in (AppointmentStatus.AGENDADA, AppointmentStatus.REAGENDADA)
        )
        if active_count >= self.max_active_appointments:
            raise DomainError(
                f"El paciente ya tiene {active_count} cita(s) activa(s). No puede agendar más de {self.max_active_appointments} simultáneamente."
            )