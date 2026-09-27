"""Pruebas de la generación de franjas (Factory Method) y de los endpoints de disponibilidad."""
from dataclasses import dataclass
from datetime import date, datetime, time

import pytest

from app.modules.appointment.domain.entities import AppointmentStatus
from app.modules.medical_staff.domain.factory.availability_generator import (
    StandardAvailabilityGenerator,
    StandardGeneratorFactory,
)
from tests.scheduling_helpers import CARLOS_ID, CHIRO, GENERAL, PHYSIO, book, create_clinic

EIGHT_SLOTS = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30"]


@dataclass
class Hours:
    start_time: time
    end_time: time
    interval_minutes: int


# ---------------------------------------------------------------- Generador


def test_factory_creates_the_standard_generator():
    assert isinstance(StandardGeneratorFactory().get_generator(), StandardAvailabilityGenerator)


def test_only_slots_that_fit_in_the_shift_are_generated():
    slots = StandardAvailabilityGenerator().generate(Hours(time(8, 0), time(10, 0), 45), set())

    assert [slot.time for slot in slots] == [time(8, 0), time(8, 45)]


def test_occupied_slots_are_flagged_and_past_ones_dropped():
    slots = StandardAvailabilityGenerator().generate(
        Hours(time(8, 0), time(10, 0), 30), occupied={time(9, 30)}, not_before=time(8, 40)
    )

    assert [(slot.time, slot.available) for slot in slots] == [(time(9, 0), True), (time(9, 30), False)]


# ---------------------------------------------------------------- Endpoints


@pytest.fixture()
def clinic(client, db_session, clock):
    create_clinic(db_session)
    return client


def _availability(client, doctor_id, on_date):
    return client.get("/api/v1/medical/availability", params={"doctor_id": doctor_id, "date": on_date}).json()


def test_day_availability_marks_occupied_slots(clinic, db_session):
    book(db_session, CARLOS_ID, GENERAL, date(2026, 3, 10), time(9, 0))
    book(db_session, CARLOS_ID, GENERAL, date(2026, 3, 10), time(10, 0), AppointmentStatus.CANCELADA)

    body = _availability(clinic, GENERAL, "2026-03-10")

    assert body["intervalMinutes"] == 30
    assert [slot["time"] for slot in body["slots"]] == EIGHT_SLOTS
    assert [slot["time"] for slot in body["slots"] if not slot["available"]] == ["09:00"]


def test_today_only_offers_slots_that_have_not_started(clinic, clock):
    clock.set(datetime(2026, 3, 9, 10, 5))

    body = _availability(clinic, GENERAL, "2026-03-09")

    assert [slot["time"] for slot in body["slots"]] == ["10:30", "11:00", "11:30"]


@pytest.mark.parametrize("on_date", ["2026-03-14", "2026-03-23", "2026-04-07", "2026-03-06"],
                         ids=["sabado", "festivo", "fuera-de-ventana", "pasado"])
def test_days_without_service_have_no_slots(clinic, on_date):
    body = _availability(clinic, GENERAL, on_date)

    assert body == {"doctorId": GENERAL, "date": on_date, "intervalMinutes": None, "slots": []}


def test_calendar_lists_bookable_days_with_free_slots(clinic, db_session):
    for start in (time(8, 0) , time(8, 30), time(9, 0), time(9, 30), time(10, 0), time(10, 30), time(11, 0), time(11, 30)):
        book(db_session, CARLOS_ID, GENERAL, date(2026, 3, 11), start)

    body = clinic.get("/api/v1/medical/availability/calendar", params={"doctor_id": GENERAL}).json()

    days = {day["date"]: day["availableSlots"] for day in body["days"]}
    assert body["lastBookableDate"] == "2026-04-06"
    assert days["2026-03-10"] == 8
    assert days["2026-03-11"] == 0  # agenda llena
    assert "2026-03-14" not in days  # sábado
    assert "2026-03-23" not in days  # festivo
    assert "2026-04-02" not in days and "2026-04-03" not in days  # Semana Santa
    assert max(days) == "2026-04-06"


def test_available_doctors_show_their_next_free_date(clinic):
    body = clinic.get("/api/v1/medical/doctors/available", params={"specialty": "Medicina General"}).json()

    assert body == [
        {"doctorId": GENERAL, "fullName": "Dra. Laura Muñoz", "specialty": "Medicina General", "nextAvailableDate": "2026-03-09"}
    ]


def test_doctor_without_schedule_has_no_next_date(clinic):
    body = clinic.get("/api/v1/medical/doctors/available", params={"specialty": "Quiropraxia"}).json()

    assert [(d["doctorId"], d["nextAvailableDate"]) for d in body] == [(CHIRO, None)]


def test_doctors_can_be_filtered_by_specialty(clinic):
    body = clinic.get("/api/v1/medical/doctors", params={"specialty": "Fisioterapia"}).json()

    assert [doctor["doctorId"] for doctor in body] == [PHYSIO]


def test_doctor_schedule_comes_from_the_configuration(clinic):
    body = clinic.get(f"/api/v1/medical/doctors/{GENERAL}/schedule").json()

    assert [day["dayOfWeek"] for day in body] == [1, 2, 3, 4, 5]
    assert body[0]["intervalMinutes"] == 30
