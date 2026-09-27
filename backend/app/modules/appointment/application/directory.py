"""
Interfaz pública del módulo `appointment` para el resto del monolito.

El módulo de personal médico calcula las franjas libres a partir de las horas que ya están
ocupadas, sin leer directamente las tablas del schema `appointment`.
"""
from collections import defaultdict
from datetime import date, time

from app.modules.appointment.infrastructure.repository import AppointmentRepository


class AppointmentDirectory:
    def __init__(self, repository: AppointmentRepository):
        self._repository = repository

    def occupied_times(self, doctor_id: int, date_from: date, date_to: date) -> dict[date, set[time]]:
        """Horas de inicio con cita activa, por fecha. Las canceladas liberan la franja."""
        occupied: dict[date, set[time]] = defaultdict(set)
        for appointment in self._repository.find_by_doctor_between(doctor_id, date_from, date_to):
            if appointment.is_active:
                occupied[appointment.date].add(appointment.start_time)
        return dict(occupied)
