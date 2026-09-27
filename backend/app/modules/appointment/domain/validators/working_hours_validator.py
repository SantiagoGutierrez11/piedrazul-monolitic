from datetime import time

from app.core.exceptions import ValidationError
from app.modules.appointment.domain.entities import Appointment
from app.modules.appointment.domain.ports import ScheduleLookup
from app.modules.appointment.domain.validators.base import AppointmentValidator


class WorkingHoursValidator(AppointmentValidator):
    """
    La cita debe coincidir con una franja del horario configurado del profesional: el día en que
    atiende, dentro de su jornada, alineada al intervalo entre citas y con esa misma duración.
    """

    def __init__(self, schedules: ScheduleLookup):
        self._schedules = schedules

    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        hours = self._schedules.working_hours_on(appointment.doctor_id, appointment.date)
        if hours is None:
            raise ValidationError("El profesional no atiende ese día. Elige otra fecha.")

        start = _minutes(appointment.start_time)
        opening, closing = _minutes(hours.start_time), _minutes(hours.end_time)
        fits_in_shift = opening <= start and start + hours.interval_minutes <= closing
        on_grid = (start - opening) % hours.interval_minutes == 0
        right_length = _minutes(appointment.end_time) - start == hours.interval_minutes

        if not (fits_in_shift and on_grid and right_length):
            raise ValidationError(
                "El profesional no atiende en ese horario. Elige una de las franjas disponibles."
            )


def _minutes(moment: time) -> int:
    return moment.hour * 60 + moment.minute
