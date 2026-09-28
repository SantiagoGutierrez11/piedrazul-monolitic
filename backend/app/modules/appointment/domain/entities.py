"""
Entidades de dominio de citas médicas.

Aquí viven las invariantes de negocio (p. ej. `cancel()`, `mark_as_attended()`),
no en los routers ni en los servicios de aplicación.
"""
import calendar
from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum

from app.core.exceptions import ConflictError, ValidationError


class ServiceType(str, Enum):
    """Servicios que ofrece Piedrazul; cada uno lo presta una especialidad."""

    CONSULTA_GENERAL = "CONSULTA_GENERAL"
    FISIOTERAPIA = "FISIOTERAPIA"
    QUIROPRAXIA = "QUIROPRAXIA"
    TERAPIA_NEURAL = "TERAPIA_NEURAL"

    @property
    def label(self) -> str:
        return _SERVICE_LABELS[self]

    @property
    def specialty(self) -> str:
        """Especialidad del profesional que presta el servicio."""
        return _SERVICE_SPECIALTIES[self]

    @property
    def requires_authorization(self) -> bool:
        """Los servicios especializados exigen que un médico los autorice en una Consulta General."""
        return self is not ServiceType.CONSULTA_GENERAL


_SERVICE_LABELS = {
    ServiceType.CONSULTA_GENERAL: "Consulta General",
    ServiceType.FISIOTERAPIA: "Fisioterapia",
    ServiceType.QUIROPRAXIA: "Quiropraxia",
    ServiceType.TERAPIA_NEURAL: "Terapia Neural",
}

_SERVICE_SPECIALTIES = {
    ServiceType.CONSULTA_GENERAL: "Medicina General",
    ServiceType.FISIOTERAPIA: "Fisioterapia",
    ServiceType.QUIROPRAXIA: "Quiropraxia",
    ServiceType.TERAPIA_NEURAL: "Terapia Neural",
}


class AppointmentStatus(str, Enum):
    AGENDADA = "AGENDADA"
    REAGENDADA = "REAGENDADA"
    ATENDIDA = "ATENDIDA"
    CANCELADA = "CANCELADA"


ACTIVE_STATUSES = frozenset({AppointmentStatus.AGENDADA, AppointmentStatus.REAGENDADA})


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

    @property
    def is_active(self) -> bool:
        return self.status in ACTIVE_STATUSES

    def schedule(self) -> None:
        """Transición usada por el agendamiento manual y el autónomo."""
        self.status = AppointmentStatus.AGENDADA

    def reschedule(self) -> None:
        self.status = AppointmentStatus.REAGENDADA

    def cancel(self) -> None:
        if self.status == AppointmentStatus.CANCELADA:
            raise ConflictError("La cita ya está cancelada")
        if self.status == AppointmentStatus.ATENDIDA:
            raise ConflictError("No se puede cancelar una cita que ya fue atendida")
        self.status = AppointmentStatus.CANCELADA

    def mark_as_attended(self, today: date) -> None:
        if self.status == AppointmentStatus.CANCELADA:
            raise ConflictError("No se puede atender una cita cancelada")
        if self.status == AppointmentStatus.ATENDIDA:
            raise ConflictError("La cita ya fue atendida")
        if self.date != today:
            raise ValidationError("Solo se puede marcar como atendida el mismo día de la cita")
        self.status = AppointmentStatus.ATENDIDA


@dataclass
class PatientAuthorization:
    """
    Autorización que un médico otorga al atender una Consulta General para que el paciente
    pueda agendar un servicio especializado. Se usa una sola vez y caduca al mes.
    """

    patient_id: int
    service_type: ServiceType
    authorized_at: datetime
    expires_at: datetime
    authorized_by_doctor_id: int
    appointment_id: int
    used: bool = False
    authorization_id: int | None = None

    @classmethod
    def grant(cls, appointment: Appointment, service_type: ServiceType, now: datetime) -> "PatientAuthorization":
        if not service_type.requires_authorization:
            raise ValidationError("La Consulta General no requiere autorización")
        return cls(
            patient_id=appointment.patient_id,
            service_type=service_type,
            authorized_at=now,
            expires_at=_one_month_after(now),
            authorized_by_doctor_id=appointment.doctor_id,
            appointment_id=appointment.appointment_id,
        )

    def is_active(self, now: datetime) -> bool:
        return not self.used and now < self.expires_at

    def mark_used(self) -> None:
        self.used = True


def _one_month_after(moment: datetime) -> datetime:
    year, month = (moment.year + 1, 1) if moment.month == 12 else (moment.year, moment.month + 1)
    day = min(moment.day, calendar.monthrange(year, month)[1])
    return moment.replace(year=year, month=month, day=day)
