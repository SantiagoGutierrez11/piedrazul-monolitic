"""
Contratos que el dominio de citas necesita de otros módulos o de su propia persistencia.

Se definen como Protocol (tipado estructural): los módulos `medical_staff`, `patient` y
`configuration` los cumplen con sus interfaces públicas sin depender de este módulo.
"""
from datetime import date, datetime, time
from typing import Protocol

from app.modules.appointment.domain.entities import Appointment, PatientAuthorization


class DoctorInfo(Protocol):
    full_name: str
    specialty: str
    active: bool


class DoctorLookup(Protocol):
    """Implementado por `medical_staff` (DoctorDirectory)."""

    def find(self, doctor_id: int) -> DoctorInfo | None: ...


class PatientLookup(Protocol):
    """Implementado por `patient` (PatientDirectory)."""

    def exists(self, patient_id: int) -> bool: ...

    def find_id_by_user(self, user_id: str) -> int | None: ...


class WorkingHoursInfo(Protocol):
    start_time: time
    end_time: time
    interval_minutes: int


class ScheduleLookup(Protocol):
    """Implementado por `configuration` (ConfigurationDirectory)."""

    def appointment_window_weeks(self) -> int: ...

    def working_hours_on(self, doctor_id: int, on_date: date) -> WorkingHoursInfo | None: ...


class PatientAppointments(Protocol):
    """Citas del propio paciente; lo implementa el repositorio de citas."""

    def find_active_by_patient(self, patient_id: int, from_date: date) -> list[Appointment]: ...


class AuthorizationStore(Protocol):
    """Autorizaciones médicas; lo implementa el repositorio de autorizaciones."""

    def find_active(self, patient_id: int, now: datetime) -> PatientAuthorization | None: ...

    def save(self, authorization: PatientAuthorization) -> PatientAuthorization: ...
