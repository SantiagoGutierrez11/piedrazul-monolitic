"""Cálculo de las franjas y los días disponibles de un profesional para el agendamiento."""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Protocol

from app.modules.medical_staff.domain.factory.availability_generator import (
    AvailabilityGeneratorFactory,
    AvailabilitySlot,
)
from app.shared.clock import Clock
from app.shared.holidays import ColombianHolidays


class WorkingDay(Protocol):
    day_of_week: int  # 1 = lunes ... 7 = domingo
    start_time: time
    end_time: time
    interval_minutes: int


class ScheduleLookup(Protocol):
    """Contrato que el módulo `configuration` expone con el horario de cada profesional."""

    def appointment_window_weeks(self) -> int: ...

    def working_hours(self, doctor_id: int) -> list[WorkingDay]: ...


class OccupancyLookup(Protocol):
    """Contrato que el módulo `appointment` expone con las horas ya reservadas."""

    def occupied_times(self, doctor_id: int, date_from: date, date_to: date) -> dict[date, set[time]]: ...


@dataclass(frozen=True)
class DayAvailability:
    date: date
    interval_minutes: int | None
    slots: list[AvailabilitySlot]


@dataclass(frozen=True)
class CalendarDay:
    date: date
    available_slots: int


class AvailabilityService:
    def __init__(
        self,
        schedules: ScheduleLookup,
        occupancy: OccupancyLookup,
        factory: AvailabilityGeneratorFactory,
        clock: Clock,
        holidays: ColombianHolidays | None = None,
    ):
        self._schedules = schedules
        self._occupancy = occupancy
        self._generator = factory.get_generator()
        self._clock = clock
        self._holidays = holidays or ColombianHolidays()

    def last_bookable_date(self) -> date:
        return self._clock.now().date() + timedelta(weeks=self._schedules.appointment_window_weeks())

    def for_date(self, doctor_id: int, on_date: date) -> DayAvailability:
        window = _Window(self._clock.now(), self.last_bookable_date())
        occupied = self._occupancy.occupied_times(doctor_id, on_date, on_date)
        return self._day(on_date, self._weekly_hours(doctor_id), occupied.get(on_date, set()), window)

    def calendar(self, doctor_id: int) -> list[CalendarDay]:
        """Días de la ventana de agendamiento en que el profesional atiende, con sus cupos libres."""
        window = _Window(self._clock.now(), self.last_bookable_date())
        weekly_hours = self._weekly_hours(doctor_id)
        occupied = self._occupancy.occupied_times(doctor_id, window.today, window.last)

        days = []
        for offset in range((window.last - window.today).days + 1):
            on_date = window.today + timedelta(days=offset)
            day = self._day(on_date, weekly_hours, occupied.get(on_date, set()), window)
            if day.interval_minutes is not None:
                free = sum(slot.available for slot in day.slots)
                days.append(CalendarDay(date=on_date, available_slots=free))
        return days

    def next_available_date(self, doctor_id: int) -> date | None:
        return next((day.date for day in self.calendar(doctor_id) if day.available_slots), None)

    def _weekly_hours(self, doctor_id: int) -> dict[int, WorkingDay]:
        return {hours.day_of_week: hours for hours in self._schedules.working_hours(doctor_id)}

    def _day(
        self,
        on_date: date,
        weekly_hours: dict[int, WorkingDay],
        occupied: set[time],
        window: "_Window",
    ) -> DayAvailability:
        hours = weekly_hours.get(on_date.isoweekday())
        if hours is None or not window.contains(on_date) or self._holidays.is_holiday(on_date):
            return DayAvailability(date=on_date, interval_minutes=None, slots=[])

        not_before = window.now.time() if on_date == window.today else None
        slots = self._generator.generate(hours, occupied, not_before)
        return DayAvailability(date=on_date, interval_minutes=hours.interval_minutes, slots=slots)


@dataclass(frozen=True)
class _Window:
    """Desde hoy hasta la última fecha que permite la ventana de agendamiento."""

    now: datetime
    last: date

    @property
    def today(self) -> date:
        return self.now.date()

    def contains(self, on_date: date) -> bool:
        return self.today <= on_date <= self.last
