from datetime import timedelta

from app.core.exceptions import ValidationError
from app.modules.appointment.domain.entities import Appointment
from app.modules.appointment.domain.ports import ScheduleLookup
from app.modules.appointment.domain.validators.base import AppointmentValidator
from app.shared.clock import Clock


class AppointmentWindowValidator(AppointmentValidator):
    """La fecha debe estar dentro de la ventana de agendamiento configurada por el administrador."""

    def __init__(self, schedules: ScheduleLookup, clock: Clock):
        self._schedules = schedules
        self._clock = clock

    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        weeks = self._schedules.appointment_window_weeks()
        last_date = self._clock.now().date() + timedelta(weeks=weeks)
        if appointment.date > last_date:
            raise ValidationError(
                f"Solo puedes agendar citas con hasta {weeks} semana(s) de anticipación. "
                f"Fecha máxima: {last_date:%d/%m/%Y}."
            )
