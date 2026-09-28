"""
Festivos de Colombia: fijos, trasladables al lunes (Ley Emiliani) y los que dependen de la Pascua.

Lo usan el módulo de citas (no se agenda en festivos) y el de personal médico (no se ofrecen
franjas en festivos), por eso vive en el núcleo compartido.
"""
from datetime import date, timedelta
from functools import lru_cache


class ColombianHolidays:
    def is_holiday(self, day: date) -> bool:
        return day in holidays_for_year(day.year)


@lru_cache(maxsize=16)
def holidays_for_year(year: int) -> frozenset[date]:
    fixed = [date(year, 1, 1), date(year, 5, 1), date(year, 7, 20), date(year, 8, 7), date(year, 12, 8), date(year, 12, 25)]
    movable = [
        date(year, 1, 6),    # Reyes Magos
        date(year, 3, 19),   # San José
        date(year, 6, 29),   # San Pedro y San Pablo
        date(year, 8, 15),   # Asunción de la Virgen
        date(year, 10, 12),  # Día de la Raza
        date(year, 11, 1),   # Todos los Santos
        date(year, 11, 11),  # Independencia de Cartagena
    ]
    easter = _easter_sunday(year)
    holy_week = [easter - timedelta(days=3), easter - timedelta(days=2)]
    easter_based = [
        easter + timedelta(days=39),  # Ascensión del Señor
        easter + timedelta(days=60),  # Corpus Christi
        easter + timedelta(days=68),  # Sagrado Corazón
    ]
    return frozenset(
        fixed + holy_week + [_next_monday(day) for day in movable + easter_based]
    )


def _next_monday(day: date) -> date:
    return day + timedelta(days=(7 - day.weekday()) % 7)


def _easter_sunday(year: int) -> date:
    """Algoritmo de Meeus/Jones/Butcher para el calendario gregoriano."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)
