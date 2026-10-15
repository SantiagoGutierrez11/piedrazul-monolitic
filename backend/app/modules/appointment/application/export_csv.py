"""
Exportación a CSV de la agenda de un profesional en una fecha (E5-HU4).

El archivo es el listado que el personal usa durante la jornada para organizar el ingreso de
los pacientes a consulta, así que se abre en Excel tal cual, sin pasos de importación.
"""
import csv
import io
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.security import CurrentUser, Role
from app.modules.appointment.application.list_appointments import (
    AppointmentWithPatient,
    ListAppointments,
)
from app.modules.appointment.domain.entities import AppointmentStatus
from app.modules.medical_staff.application.directory import DoctorSummary

# ---------------------------------------------------------------- Columnas (2.1)

COLUMNS = ("Hora", "Paciente", "Documento", "Teléfono", "Servicio", "Estado")

# ---------------------------------------------------------------- Formato del archivo (2.2)

# Punto y coma porque Excel en español (configuración regional de Colombia) usa la coma como
# separador decimal y espera ";" como separador de columnas.
SEPARATOR = ";"
# UTF-8 con BOM: sin él Excel abre el archivo como ANSI y daña las tildes y las eñes.
ENCODING = "utf-8-sig"
MEDIA_TYPE = "text/csv; charset=utf-8"

# Excel ejecuta como fórmula una celda que empieza por estos caracteres (inyección CSV, OWASP).
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")
# Un teléfono como "+57 310 987 6543" empieza por "+" pero no es una fórmula.
_PHONE = re.compile(r"\+?[\d ]+")


def filename(doctor_name: str, on_date: date) -> str:
    """Por ejemplo `citas_juan-perez_2026-03-09.csv`: sin tildes ni espacios."""
    plain = unicodedata.normalize("NFKD", doctor_name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-") or "profesional"
    return f"citas_{slug}_{on_date.isoformat()}.csv"


# ---------------------------------------------------------------- Quién exporta y qué citas (2.3)

EXPORT_ROLES = (Role.MEDICO, Role.AGENDADOR, Role.ADMINISTRADOR)

# Las canceladas no forman parte del listado de ingreso de la jornada.
EXCLUDED_STATUSES = frozenset({AppointmentStatus.CANCELADA})


def ensure_can_export(user: CurrentUser, doctor_id: int, own_doctor_id: int | None) -> None:
    """
    Agendador y administrador exportan la agenda de cualquier profesional; el médico solo la
    suya (`own_doctor_id` es el profesional asociado a su cuenta).
    """
    if user.has_any((Role.AGENDADOR, Role.ADMINISTRADOR)):
        return
    if Role.MEDICO in user.roles and own_doctor_id == doctor_id:
        return
    raise ForbiddenError("Solo puedes exportar tu propia agenda")


def exportable(listing: list[AppointmentWithPatient]) -> list[AppointmentWithPatient]:
    """Citas que van en el archivo, en orden de llegada a consulta."""
    included = [item for item in listing if item.appointment.status not in EXCLUDED_STATUSES]
    return sorted(included, key=lambda item: item.appointment.start_time)


def to_csv(listing: list[AppointmentWithPatient]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=SEPARATOR, lineterminator="\r\n")
    writer.writerow(COLUMNS)
    for item in listing:
        writer.writerow([_safe_cell(value) for value in _row(item)])
    return buffer.getvalue().encode(ENCODING)


def _row(item: AppointmentWithPatient) -> tuple[str, ...]:
    appointment, patient = item.appointment, item.patient
    return (
        appointment.start_time.strftime("%H:%M"),
        patient.full_name if patient else "Paciente sin registrar",
        patient.document if patient else "",
        patient.phone if patient else "",
        appointment.service_type.label,
        appointment.status.value.capitalize(),
    )


def _safe_cell(value: str) -> str:
    if value.startswith(_FORMULA_PREFIXES) and not _PHONE.fullmatch(value):
        return f"'{value}"
    return value


# ---------------------------------------------------------------- Caso de uso (3.1)


class DoctorLookup(Protocol):
    """Contrato que el módulo `medical_staff` expone para resolver al profesional."""

    def find(self, doctor_id: int) -> DoctorSummary | None: ...

    def find_id_by_user(self, user_id: str) -> int | None: ...


@dataclass(frozen=True)
class CsvFile:
    filename: str
    content: bytes


class ExportAgendaCsv:
    def __init__(self, appointments: ListAppointments, doctors: DoctorLookup):
        self._appointments = appointments
        self._doctors = doctors

    def execute(self, user: CurrentUser, doctor_id: int, on_date: date) -> CsvFile | None:
        """Archivo con la agenda, o `None` si el profesional no tiene citas que exportar ese día."""
        own_doctor_id = self._doctors.find_id_by_user(user.user_id) if Role.MEDICO in user.roles else None
        ensure_can_export(user, doctor_id, own_doctor_id)

        doctor = self._doctors.find(doctor_id)
        if doctor is None:
            raise NotFoundError("El profesional no existe")

        listing = exportable(self._appointments.by_doctor_and_date(doctor_id, on_date))
        if not listing:
            return None
        return CsvFile(filename=filename(doctor.full_name, on_date), content=to_csv(listing))
