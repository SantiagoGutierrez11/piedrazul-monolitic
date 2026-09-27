from datetime import datetime
from app.core.exceptions import ValidationError
from app.modules.appointment.domain.entities import Appointment
from app.modules.appointment.domain.validators.base import AppointmentValidator


class DataAppointmentValidator(AppointmentValidator):
    """Valida la coherencia de datos, fechas futuras y duración."""

    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        now = datetime.now()
        appointment_datetime = datetime.combine(appointment.date, appointment.start_time)

        if appointment_datetime <= now:
            raise ValidationError("No se puede agendar una cita en una fecha u hora pasada.")

        if appointment.start_time >= appointment.end_time:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

        if not appointment.reason or len(appointment.reason.strip()) < 5:
            raise ValidationError("Debe proporcionar un motivo válido para la cita (mínimo 5 caracteres).")