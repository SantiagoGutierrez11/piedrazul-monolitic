"""
Entidades de dominio de citas médicas.

Aquí es donde deben vivir las invariantes de negocio (p. ej. `cancel()`, `mark_as_attended()`),
no en los routers ni en los servicios de aplicación.
"""
from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum


class ServiceType(str, Enum):
    CONSULTA_GENERAL = "CONSULTA_GENERAL"
    FISIOTERAPIA = "FISIOTERAPIA"
    QUIROPRAXIA = "QUIROPRAXIA"
    TERAPIA_NEURAL = "TERAPIA_NEURAL"


class AppointmentStatus(str, Enum):
    AGENDADA = "AGENDADA"
    REAGENDADA = "REAGENDADA"
    ATENDIDA = "ATENDIDA"
    CANCELADA = "CANCELADA"


@dataclass
class Appointment:
    patient_id: int
    doctor_id: int
    doctor_name: str
    service_type: ServiceType
    date: date
    start_time: time
    end_time: time
    reason: str
    notes: str = ""
    status: AppointmentStatus = AppointmentStatus.AGENDADA
    appointment_id: int | None = field(default=None)

    def schedule(self) -> None:
        """Transición usada por el agendamiento manual (y punto de partida del autónomo)."""
        self.status = AppointmentStatus.AGENDADA

    def reschedule(self) -> None:
        self.status = AppointmentStatus.REAGENDADA

    def cancel(self) -> None:
        if self.status == AppointmentStatus.ATENDIDA:
            raise ValueError("No se puede cancelar una cita ya atendida")
        self.status = AppointmentStatus.CANCELADA

    def mark_as_attended(self) -> None:
        self.status = AppointmentStatus.ATENDIDA
