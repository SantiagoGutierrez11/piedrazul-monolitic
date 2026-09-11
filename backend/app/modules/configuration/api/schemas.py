"""DTOs de entrada/salida de /api/v1/configuration."""
from datetime import time

from app.shared.schemas import CamelModel


class GlobalConfigurationResponse(CamelModel):
    weeks: int


class AppointmentWindowRequest(CamelModel):
    weeks: int


class DoctorScheduleItem(CamelModel):
    day_of_week: int
    start_time: time
    end_time: time
    interval_minutes: int


class DoctorScheduleRequest(CamelModel):
    schedules: list[DoctorScheduleItem]
