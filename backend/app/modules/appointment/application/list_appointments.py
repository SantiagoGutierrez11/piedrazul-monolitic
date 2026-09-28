"""Consultas de citas: agenda de un médico en una fecha y citas de un paciente."""
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from app.modules.appointment.domain.entities import Appointment, AppointmentStatus, ServiceType
from app.modules.appointment.infrastructure.repository import AppointmentRepository
from app.modules.patient.application.directory import PatientSummary


class PatientLookup(Protocol):
    """Contrato que el módulo `patient` expone para resolver los datos del paciente."""

    def find_summaries(self, patient_ids: set[int]) -> dict[int, PatientSummary]: ...


@dataclass
class AppointmentWithPatient:
    appointment: Appointment
    patient: PatientSummary | None


class ListAppointments:
    def __init__(self, repository: AppointmentRepository, patients: PatientLookup):
        self._repository = repository
        self._patients = patients

    def by_doctor_and_date(
        self,
        doctor_id: int,
        on_date: date,
        service_type: ServiceType | None = None,
        status: AppointmentStatus | None = None,
    ) -> list[AppointmentWithPatient]:
        appointments = [
            appointment
            for appointment in self._repository.find_by_doctor_and_date(doctor_id, on_date)
            if (service_type is None or appointment.service_type == service_type)
            and (status is None or appointment.status == status)
        ]
        return self._with_patients(appointments)

    def by_date(self, on_date: date, doctor_id: int | None = None) -> list[AppointmentWithPatient]:
        appointments = [
            appointment
            for appointment in self._repository.find_between(on_date, on_date)
            if doctor_id is None or appointment.doctor_id == doctor_id
        ]
        return self._with_patients(appointments)

    def by_patient(self, patient_id: int) -> list[AppointmentWithPatient]:
        return self._with_patients(self._repository.find_by_patient(patient_id))

    def _with_patients(self, appointments: list[Appointment]) -> list[AppointmentWithPatient]:
        summaries = self._patients.find_summaries({a.patient_id for a in appointments})
        return [
            AppointmentWithPatient(
                appointment=appointment,
                patient=summaries.get(appointment.patient_id),
            )
            for appointment in appointments
        ]
