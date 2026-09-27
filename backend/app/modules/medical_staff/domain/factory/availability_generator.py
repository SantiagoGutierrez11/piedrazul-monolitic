from abc import ABC, abstractmethod
from datetime import date, time, datetime, timedelta
from app.modules.appointment.infrastructure.repository import AppointmentRepository


class AvailabilityGenerator(ABC):
    @abstractmethod
    def generate(self, doctor_id: int, on_date: date) -> list[time]:
        raise NotImplementedError


class StandardAvailabilityGenerator(AvailabilityGenerator):
    """Genera slots de 30 minutos considerando jornada laboral y citas ocupadas."""

    def __init__(self, appointment_repository: AppointmentRepository):
        self._repository = appointment_repository

    def generate(self, doctor_id: int, on_date: date) -> list[time]:
        # 1. Traer citas ya reservadas/activas para ese médico y día
        existing_appointments = self._repository.find_by_doctor_and_date(doctor_id, on_date)
        busy_times = {
            app.start_time for app in existing_appointments
            if app.status != "CANCELADA"
        }

        # 2. Definir jornada estándar (Ejemplo: 08:00 a 12:00 y 14:00 a 17:00, slots de 30 min)
        # Nota: En producción esto se consulta desde el módulo `configuration`.
        available_slots: list[time] = []

        # Turno Mañana (08:00 - 12:00)
        current = datetime.combine(on_date, time(8, 0))
        end_morning = datetime.combine(on_date, time(12, 0))

        while current < end_morning:
            slot_time = current.time()
            if slot_time not in busy_times:
                available_slots.append(slot_time)
            current += timedelta(minutes=30)

        # Turno Tarde (14:00 - 17:00)
        current = datetime.combine(on_date, time(14, 0))
        end_afternoon = datetime.combine(on_date, time(17, 0))

        while current < end_afternoon:
            slot_time = current.time()
            if slot_time not in busy_times:
                available_slots.append(slot_time)
            current += timedelta(minutes=30)

        return available_slots


def get_availability_generator(repository: AppointmentRepository) -> AvailabilityGenerator:
    """Factory Method: Retorna la estrategia de generación de disponibilidad."""
    return StandardAvailabilityGenerator(repository)
