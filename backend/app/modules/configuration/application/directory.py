"""
Interfaz pública del módulo `configuration` para el resto del monolito.

Los módulos de citas y de personal médico consultan la ventana de agendamiento y el horario
de cada profesional solo a través de esta clase.
"""
from dataclasses import dataclass
from datetime import date, time

from app.modules.configuration.application.service import ConfigurationService
from app.modules.configuration.infrastructure.repository import ConfigurationRepository


@dataclass(frozen=True)
class WorkingHours:
    day_of_week: int  # 1 = lunes ... 7 = domingo
    start_time: time
    end_time: time
    interval_minutes: int


class ConfigurationDirectory:
    def __init__(self, repository: ConfigurationRepository):
        self._service = ConfigurationService(repository)

    def appointment_window_weeks(self) -> int:
        return self._service.get_appointment_window_weeks()

    def working_hours(self, doctor_id: int) -> list[WorkingHours]:
        return [
            WorkingHours(
                day_of_week=schedule.day_of_week,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                interval_minutes=schedule.interval_minutes,
            )
            for schedule in self._service.get_doctor_schedule(doctor_id)
        ]

    def working_hours_on(self, doctor_id: int, on_date: date) -> WorkingHours | None:
        weekday = on_date.isoweekday()
        return next((hours for hours in self.working_hours(doctor_id) if hours.day_of_week == weekday), None)
