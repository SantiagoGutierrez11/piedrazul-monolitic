"""
Template Method para el flujo de agendamiento.

execute() define el esqueleto fijo (buscar existentes, validar, asignar estado, guardar,
publicar evento); el paso variable `_assign_status` lo define cada subclase concreta
(ver manual_scheduling.py y autonomous_scheduling.py).
"""
from abc import ABC, abstractmethod

from app.core.event_bus import publish
from app.modules.appointment.domain.entities import Appointment
from app.modules.appointment.domain.validators.base import AppointmentValidator
from app.modules.appointment.infrastructure.repository import AppointmentRepository


class AppointmentSchedulingTemplate(ABC):
    def __init__(self, repository: AppointmentRepository, validators: list[AppointmentValidator]):
        self._repository = repository
        self._validators = validators

    def execute(self, appointment: Appointment) -> Appointment:
        existing_on_date = self._repository.find_by_doctor_and_date(
            appointment.doctor_id, appointment.date
        )
        for validator in self._validators:
            validator.validate(appointment, existing_on_date)

        self._assign_status(appointment)
        saved = self._repository.save(appointment)
        publish("appointment.scheduled", {"appointment_id": saved.appointment_id})
        return saved

    @abstractmethod
    def _assign_status(self, appointment: Appointment) -> None:
        raise NotImplementedError
