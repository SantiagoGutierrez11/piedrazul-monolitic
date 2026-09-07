"""
TODO: implementar sobre SQLAlchemy contra el schema `appointment` (ver core/database.py).
Las firmas ya coinciden con lo que necesita application/ (listar, autónomo/manual).
"""
from datetime import date

from app.modules.appointment.domain.entities import Appointment


class AppointmentRepository:
    def find_by_doctor_and_date(self, doctor_id: int, on_date: date) -> list[Appointment]:
        raise NotImplementedError

    def find_by_id(self, appointment_id: int) -> Appointment | None:
        raise NotImplementedError

    def find_by_patient(self, patient_id: int) -> list[Appointment]:
        raise NotImplementedError

    def save(self, appointment: Appointment) -> Appointment:
        raise NotImplementedError
