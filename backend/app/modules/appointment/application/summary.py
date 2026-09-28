"""Indicadores de citas para los paneles del agendador y del administrador."""
from dataclasses import dataclass
from datetime import date, timedelta

from app.modules.appointment.domain.entities import AppointmentStatus
from app.modules.appointment.infrastructure.repository import AppointmentRepository
from app.shared.clock import Clock


@dataclass(frozen=True)
class DayCount:
    date: date
    count: int


@dataclass(frozen=True)
class AppointmentSummary:
    today: int
    pending: int
    week: list[DayCount]


class AppointmentSummaryQuery:
    def __init__(self, repository: AppointmentRepository, clock: Clock):
        self._repository = repository
        self._clock = clock

    def execute(self) -> AppointmentSummary:
        today = self._clock.now().date()
        monday = today - timedelta(days=today.weekday())
        week_days = [monday + timedelta(days=offset) for offset in range(7)]  # lunes a domingo

        counts = {day: 0 for day in week_days}
        for appointment in self._repository.find_between(week_days[0], week_days[-1]):
            if appointment.status != AppointmentStatus.CANCELADA:
                counts[appointment.date] += 1

        return AppointmentSummary(
            today=counts[today],
            pending=self._repository.count_active_from(today),
            week=[DayCount(date=day, count=counts[day]) for day in week_days],
        )
