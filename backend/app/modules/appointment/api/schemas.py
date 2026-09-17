"""DTOs de entrada/salida de /api/v1/appointments."""
from datetime import date, time

from app.modules.appointment.domain.entities import AppointmentStatus, ServiceType
from app.shared.schemas import CamelModel


class AppointmentResponse(CamelModel):
    appointment_id: int
    patient_id: int
    doctor_id: int
    doctor_name: str
    service_type: ServiceType
    date: date
    start_time: time
    end_time: time
    reason: str
    notes: str = ""
    status: AppointmentStatus
