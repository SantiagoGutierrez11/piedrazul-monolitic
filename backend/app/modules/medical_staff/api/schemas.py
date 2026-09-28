"""DTOs de entrada/salida de /api/v1/medical."""
from datetime import date, time

from app.modules.medical_staff.application.availability import CalendarDay, DayAvailability
from app.shared.schemas import CamelModel


class DoctorResponse(CamelModel):
    doctor_id: int
    full_name: str
    specialty: str


class AvailableDoctorResponse(DoctorResponse):
    # Primera fecha con cupo dentro de la ventana de agendamiento; None si no hay.
    next_available_date: date | None


class WorkingHoursResponse(CamelModel):
    day_of_week: int
    start_time: time
    end_time: time
    interval_minutes: int


class SlotResponse(CamelModel):
    time: str  # HH:MM
    available: bool


class AvailabilityResponse(CamelModel):
    doctor_id: int
    date: date
    interval_minutes: int | None
    slots: list[SlotResponse]

    @classmethod
    def from_day(cls, doctor_id: int, day: DayAvailability) -> "AvailabilityResponse":
        return cls(
            doctor_id=doctor_id,
            date=day.date,
            interval_minutes=day.interval_minutes,
            slots=[SlotResponse(time=f"{s.time:%H:%M}", available=s.available) for s in day.slots],
        )


class CalendarDayResponse(CamelModel):
    date: date
    available_slots: int


class CalendarResponse(CamelModel):
    doctor_id: int
    last_bookable_date: date
    days: list[CalendarDayResponse]

    @classmethod
    def from_days(cls, doctor_id: int, last: date, days: list[CalendarDay]) -> "CalendarResponse":
        return cls(
            doctor_id=doctor_id,
            last_bookable_date=last,
            days=[CalendarDayResponse(date=d.date, available_slots=d.available_slots) for d in days],
        )
