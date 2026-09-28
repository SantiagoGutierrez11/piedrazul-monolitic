from app.core.exceptions import ValidationError
from app.modules.appointment.domain.entities import Appointment
from app.modules.appointment.domain.validators.base import AppointmentValidator
from app.shared.holidays import ColombianHolidays


class HolidayValidator(AppointmentValidator):
    """No se agendan citas en festivos colombianos."""

    def __init__(self, holidays: ColombianHolidays):
        self._holidays = holidays

    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        if self._holidays.is_holiday(appointment.date):
            raise ValidationError(
                "No se pueden agendar citas en días festivos. Por favor selecciona otra fecha."
            )
