"""Casos de uso de configuración del sistema."""
from app.core.event_bus import publish
from app.core.exceptions import ValidationError
from app.modules.configuration.domain.entities import DoctorScheduleConfiguration, SystemParameter
from app.modules.configuration.infrastructure.repository import ConfigurationRepository

DEFAULT_APPOINTMENT_WINDOW_WEEKS = 4
APPOINTMENT_WINDOW_KEY = "appointment_window_weeks"


class ConfigurationService:
    def __init__(self, repository: ConfigurationRepository):
        self._repository = repository

    def get_appointment_window_weeks(self) -> int:
        parameter = self._repository.find_parameter(APPOINTMENT_WINDOW_KEY)
        if parameter is None:
            return DEFAULT_APPOINTMENT_WINDOW_WEEKS
        return int(parameter.value)

    def update_appointment_window_weeks(self, weeks: int) -> int:
        if not (1 <= weeks <= 52):
            raise ValidationError("La ventana de tiempo debe estar entre 1 y 52 semanas")

        self._repository.save_parameter(
            SystemParameter(
                key=APPOINTMENT_WINDOW_KEY,
                value=str(weeks),
                description="Semanas hacia adelante en las que se puede agendar una cita",
            )
        )
        publish("configuration.appointment_window_updated", {"weeks": weeks})
        return weeks

    def get_doctor_schedule(self, doctor_id: int) -> list[DoctorScheduleConfiguration]:
        return self._repository.find_schedule_by_doctor(doctor_id)

    def update_doctor_schedule(
        self, doctor_id: int, schedules: list[DoctorScheduleConfiguration]
    ) -> list[DoctorScheduleConfiguration]:
        self._validate_schedules(schedules)
        saved = self._repository.replace_schedule(doctor_id, schedules)
        publish("configuration.doctor_schedule_updated", {"doctor_id": doctor_id})
        return saved

    @staticmethod
    def _validate_schedules(schedules: list[DoctorScheduleConfiguration]) -> None:
        seen_days: set[int] = set()
        for schedule in schedules:
            if not (1 <= schedule.day_of_week <= 7):
                raise ValidationError("El día de la semana debe estar entre 1 (lunes) y 7 (domingo)")
            if schedule.day_of_week in seen_days:
                raise ValidationError("No puede haber dos franjas para el mismo día de la semana")
            seen_days.add(schedule.day_of_week)

            if schedule.start_time >= schedule.end_time:
                raise ValidationError("La hora de inicio debe ser anterior a la hora de fin")
            if schedule.interval_minutes <= 0:
                raise ValidationError("El intervalo entre citas debe ser mayor a cero")

            minutes_available = (
                schedule.end_time.hour * 60
                + schedule.end_time.minute
                - schedule.start_time.hour * 60
                - schedule.start_time.minute
            )
            if schedule.interval_minutes > minutes_available:
                raise ValidationError(
                    "El intervalo entre citas no puede superar la duración de la franja de atención"
                )
