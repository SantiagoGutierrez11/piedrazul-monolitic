"""Festivos colombianos: fijos, trasladables (Ley Emiliani) y basados en la Pascua."""
from datetime import date

from app.shared.holidays import ColombianHolidays, holidays_for_year

OFFICIAL_2026 = {
    date(2026, 1, 1), date(2026, 1, 12), date(2026, 3, 23), date(2026, 4, 2), date(2026, 4, 3),
    date(2026, 5, 1), date(2026, 5, 18), date(2026, 6, 8), date(2026, 6, 15), date(2026, 6, 29),
    date(2026, 7, 20), date(2026, 8, 7), date(2026, 8, 17), date(2026, 10, 12), date(2026, 11, 2),
    date(2026, 11, 16), date(2026, 12, 8), date(2026, 12, 25),
}


def test_matches_the_official_2026_calendar():
    assert holidays_for_year(2026) == OFFICIAL_2026


def test_movable_holiday_already_on_monday_is_not_moved():
    # San Pedro y San Pablo cae lunes en 2026.
    assert date(2026, 6, 29) in holidays_for_year(2026)


def test_easter_based_holidays_change_every_year():
    # Semana Santa 2027: domingo de Pascua el 28 de marzo.
    assert {date(2027, 3, 25), date(2027, 3, 26)} <= holidays_for_year(2027)


def test_regular_weekday_is_not_a_holiday():
    assert not ColombianHolidays().is_holiday(date(2026, 3, 10))
