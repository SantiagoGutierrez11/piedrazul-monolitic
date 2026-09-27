from app.core.exceptions import ConflictError
from app.modules.appointment.domain.entities import Appointment
from app.modules.appointment.domain.validators.base import AppointmentValidator


class ConflictValidator(AppointmentValidator):
    """Impide dos citas activas con el mismo médico en el mismo horario (las canceladas liberan la franja)."""

    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        for existing in existing_on_date:
            if not existing.is_active:
                continue
            same_slot = existing.start_time == appointment.start_time
            # Al reagendar, la cita no choca consigo misma.
            other_appointment = (
                appointment.appointment_id is None
                or existing.appointment_id != appointment.appointment_id
            )
            if same_slot and other_appointment:
                raise ConflictError("Ese horario ya no está disponible. Por favor elige otro.")
