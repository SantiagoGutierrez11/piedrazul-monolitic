"""
Contrato de validador (patrón Strategy/Chain).

Cada regla de negocio del agendamiento vive en su propia clase; el Template Method
(ver application/scheduling/base.py) las ejecuta en cadena antes de guardar.
"""
from abc import ABC, abstractmethod

from app.modules.appointment.domain.entities import Appointment


class AppointmentValidator(ABC):
    @abstractmethod
    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        """Lanza una excepción de dominio (ver core/exceptions.py) si la regla se incumple."""
        raise NotImplementedError
