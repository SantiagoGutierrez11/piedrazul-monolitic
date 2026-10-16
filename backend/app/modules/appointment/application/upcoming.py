"""
Próximas citas agrupadas por semana, para el reporte del médico, el agendador y el
administrador.

Cada semana va de lunes a domingo; la primera es la semana en curso y solo trae citas desde
hoy. Se incluyen las semanas sin citas para que el reporte muestre también los huecos.
"""
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.security import CurrentUser, Role
from app.modules.appointment.application.list_appointments import (
    AppointmentWithPatient,
    ListAppointments,
)
from app.shared.clock import Clock

DEFAULT_WEEKS = 4
MAX_WEEKS = 8
UPCOMING_ROLES = (Role.MEDICO, Role.AGENDADOR, Role.ADMINISTRADOR)


class DoctorAccounts(Protocol):
    """Contrato que el módulo `medical_staff` expone para saber qué profesional es el médico."""

    def find_id_by_user(self, user_id: str) -> int | None: ...


@dataclass(frozen=True)
class UpcomingWeek:
    start: date  # lunes
    end: date  # domingo
    appointments: list[AppointmentWithPatient]


@dataclass(frozen=True)
class UpcomingAppointments:
    date_from: date
    date_to: date
    weeks: list[UpcomingWeek]


class UpcomingAppointmentsQuery:
    def __init__(self, listing: ListAppointments, doctors: DoctorAccounts, clock: Clock):
        self._listing = listing
        self._doctors = doctors
        self._clock = clock

    def execute(
        self, user: CurrentUser, weeks: int = DEFAULT_WEEKS, doctor_id: int | None = None
    ) -> UpcomingAppointments:
        doctor_id = self._doctor_filter(user, doctor_id)
        today = self._clock.now().date()
        mondays = [today - timedelta(days=today.weekday()) + timedelta(weeks=n) for n in range(weeks)]
        date_to = mondays[-1] + timedelta(days=6)

        by_week: dict[date, list[AppointmentWithPatient]] = {monday: [] for monday in mondays}
        for item in self._listing.active_between(today, date_to, doctor_id):
            appointment_date = item.appointment.date
            by_week[appointment_date - timedelta(days=appointment_date.weekday())].append(item)

        return UpcomingAppointments(
            date_from=today,
            date_to=date_to,
            weeks=[
                UpcomingWeek(start=monday, end=monday + timedelta(days=6), appointments=by_week[monday])
                for monday in mondays
            ],
        )

    def _doctor_filter(self, user: CurrentUser, doctor_id: int | None) -> int | None:
        """Agendador y administrador ven todo el centro (o un profesional); el médico, solo lo suyo."""
        if user.has_any((Role.AGENDADOR, Role.ADMINISTRADOR)):
            return doctor_id
        own_doctor_id = self._doctors.find_id_by_user(user.user_id)
        if own_doctor_id is None:
            raise NotFoundError("No se encontró el perfil del profesional")
        if doctor_id is not None and doctor_id != own_doctor_id:
            raise ForbiddenError("Solo puedes ver tu propia agenda")
        return own_doctor_id
