"""Consultas de citas: agenda de un médico en una fecha y citas de un paciente."""
from datetime import date

from app.modules.appointment.domain.entities import Appointment, AppointmentStatus, ServiceType
from app.modules.appointment.infrastructure.repository import AppointmentRepository


class ListAppointments:
    def __init__(self, repository: AppointmentRepository):
        self._repository = repository

    def by_doctor_and_date(
        self,
        doctor_id: int,
        on_date: date,
        service_type: ServiceType | None = None,
        status: AppointmentStatus | None = None,
    ) -> list[Appointment]:
        appointments = self._repository.find_by_doctor_and_date(doctor_id, on_date)
        return [
            appointment
            for appointment in appointments
            if (service_type is None or appointment.service_type == service_type)
            and (status is None or appointment.status == status)
        ]

    def by_patient(self, patient_id: int) -> list[Appointment]:
        return self._repository.find_by_patient(patient_id)
