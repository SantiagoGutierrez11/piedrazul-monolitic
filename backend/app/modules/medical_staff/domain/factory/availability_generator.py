"""
Calcula los horarios (slots) disponibles de un médico en una fecha, a partir de su
configuración (module `configuration`) y las citas ya ocupadas (module `appointment`).
Usa el patrón Factory Method para poder cambiar de estrategia de generación más adelante.
Lo consume el paso "Fecha y Hora" del agendamiento autónomo.
"""
from abc import ABC, abstractmethod
from datetime import date, time


class AvailabilityGenerator(ABC):
    @abstractmethod
    def generate(self, doctor_id: int, on_date: date) -> list[time]:
        raise NotImplementedError


class StandardAvailabilityGenerator(AvailabilityGenerator):
    def generate(self, doctor_id: int, on_date: date) -> list[time]:
        """TODO: implementar el cálculo real (horario + intervalo - citas ocupadas)."""
        raise NotImplementedError


def get_availability_generator() -> AvailabilityGenerator:
    """Factory Method: punto único para cambiar de estrategia de generación si se necesita otra."""
    return StandardAvailabilityGenerator()
