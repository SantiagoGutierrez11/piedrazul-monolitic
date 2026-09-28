"""
Hora actual del negocio.

Las reglas de agendamiento dependen de "hoy" y "ahora" en Colombia, no de la zona horaria del
servidor (el contenedor corre en UTC). Los casos de uso reciben un `Clock` para que las pruebas
puedan fijar la fecha.
"""
from datetime import datetime
from typing import Protocol
from zoneinfo import ZoneInfo

from app.core.config import settings


class Clock(Protocol):
    def now(self) -> datetime:
        """Fecha y hora local, sin zona horaria adjunta."""
        ...


class SystemClock:
    def __init__(self, timezone: str = settings.timezone):
        self._zone = ZoneInfo(timezone)

    def now(self) -> datetime:
        return datetime.now(self._zone).replace(tzinfo=None)


def get_clock() -> Clock:
    return SystemClock()
