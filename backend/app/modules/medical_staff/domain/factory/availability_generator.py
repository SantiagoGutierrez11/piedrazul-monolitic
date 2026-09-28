"""
Patrón Factory Method para generar las franjas de atención de un profesional.

`AvailabilityGeneratorFactory` es el creador abstracto: quien calcula la disponibilidad pide un
generador sin saber cuál implementación concreta recibe. Hoy existe el generador estándar
(franjas de igual duración); otro tipo de horario solo requiere un nuevo par generador/fábrica.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Protocol


class WorkingHoursLike(Protocol):
    start_time: time
    end_time: time
    interval_minutes: int


@dataclass(frozen=True)
class AvailabilitySlot:
    time: time
    available: bool


class AvailabilityGenerator(ABC):
    @abstractmethod
    def generate(
        self,
        hours: WorkingHoursLike,
        occupied: set[time],
        not_before: time | None = None,
    ) -> list[AvailabilitySlot]:
        """Franjas de la jornada; `not_before` descarta las que ya pasaron el día de hoy."""


class StandardAvailabilityGenerator(AvailabilityGenerator):
    """Franjas consecutivas del mismo intervalo que caben completas dentro de la jornada."""

    def generate(
        self,
        hours: WorkingHoursLike,
        occupied: set[time],
        not_before: time | None = None,
    ) -> list[AvailabilitySlot]:
        step = timedelta(minutes=hours.interval_minutes)
        current = datetime.combine(date.min, hours.start_time)
        closing = datetime.combine(date.min, hours.end_time)

        slots = []
        while current + step <= closing:
            start = current.time()
            if not_before is None or start > not_before:
                slots.append(AvailabilitySlot(time=start, available=start not in occupied))
            current += step
        return slots


class AvailabilityGeneratorFactory(ABC):
    @abstractmethod
    def create_generator(self) -> AvailabilityGenerator:
        """Factory Method: cada fábrica concreta decide qué generador crear."""

    def get_generator(self) -> AvailabilityGenerator:
        return self.create_generator()


class StandardGeneratorFactory(AvailabilityGeneratorFactory):
    def create_generator(self) -> AvailabilityGenerator:
        return StandardAvailabilityGenerator()
