"""Entidades de configuración: parámetros del sistema y horarios por profesional."""
from dataclasses import dataclass
from datetime import time


@dataclass
class SystemParameter:
    key: str
    value: str
    description: str = ""


@dataclass
class DoctorScheduleConfiguration:
    doctor_id: int
    day_of_week: int  # 1 = Lunes ... 7 = Domingo
    start_time: time
    end_time: time
    interval_minutes: int
    id: int | None = None
