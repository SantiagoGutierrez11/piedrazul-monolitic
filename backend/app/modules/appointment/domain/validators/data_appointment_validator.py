from datetime import datetime

from app.core.exceptions import ValidationError
from app.modules.appointment.domain.entities import Appointment
from app.modules.appointment.domain.validators.base import AppointmentValidator
from app.shared.clock import Clock


class DataAppointmentValidator(AppointmentValidator):
    """Valida la coherencia de los datos: identificadores, fecha futura, duración y motivo."""

    def __init__(self, clock: Clock):
        self._clock = clock

    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        if appointment.patient_id <= 0:
            raise ValidationError("El paciente de la cita no es válido.")
        if appointment.doctor_id <= 0:
            raise ValidationError("El profesional de la cita no es válido.")

        if datetime.combine(appointment.date, appointment.start_time) <= self._clock.now():
            raise ValidationError("No se puede agendar una cita en una fecha u hora pasada.")

        if appointment.start_time >= appointment.end_time:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

        if not appointment.reason or len(appointment.reason.strip()) < 5:
            raise ValidationError("Debe proporcionar un motivo válido para la cita (mínimo 5 caracteres).")
