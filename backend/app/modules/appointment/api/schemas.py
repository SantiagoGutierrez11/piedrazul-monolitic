"""DTOs de entrada/salida de /api/v1/appointments."""
from datetime import date, time

from app.modules.appointment.application.list_appointments import AppointmentWithPatient
from app.modules.appointment.domain.entities import AppointmentStatus, ServiceType
from app.shared.schemas import CamelModel


class AppointmentResponse(CamelModel):
    appointment_id: int
    patient_id: int
    patient_name: str | None = None
    patient_phone: str | None = None
    doctor_id: int
    doctor_name: str
    service_type: ServiceType
    date: date
    start_time: time
    end_time: time
    reason: str
    notes: str = ""
    status: AppointmentStatus

    @classmethod
    def from_listing(cls, item: AppointmentWithPatient) -> "AppointmentResponse":
        appointment = item.appointment
        return cls(
            appointment_id=appointment.appointment_id,
            patient_id=appointment.patient_id,
            patient_name=item.patient.full_name if item.patient else None,
            patient_phone=item.patient.phone if item.patient else None,
            doctor_id=appointment.doctor_id,
            doctor_name=appointment.doctor_name,
            service_type=appointment.service_type,
            date=appointment.date,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            reason=appointment.reason,
            notes=appointment.notes,
            status=appointment.status,
        )
