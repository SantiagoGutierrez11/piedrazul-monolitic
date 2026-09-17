"""
Rutas montadas bajo /api/v1/appointments (ver app/main.py). Cada handler delega en un
caso de uso de application/ — el router no debe contener lógica de negocio.
"""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.appointment.api.schemas import AppointmentResponse
from app.modules.appointment.application.list_appointments import ListAppointments
from app.modules.appointment.domain.entities import AppointmentStatus, ServiceType
from app.modules.appointment.infrastructure.repository import AppointmentRepository

router = APIRouter()


def get_list_appointments(db: Session = Depends(get_db)) -> ListAppointments:
    return ListAppointments(AppointmentRepository(db))


@router.get("/doctor/{doctor_id}/date/{date}", response_model=list[AppointmentResponse])
def list_by_doctor_and_date(
    doctor_id: int,
    date: date,
    service_type: ServiceType | None = None,
    status: AppointmentStatus | None = None,
    use_case: ListAppointments = Depends(get_list_appointments),
):
    appointments = use_case.by_doctor_and_date(doctor_id, date, service_type, status)
    return [AppointmentResponse.model_validate(appointment) for appointment in appointments]


@router.get("/patient/{patient_id}", response_model=list[AppointmentResponse])
def list_by_patient(patient_id: int, use_case: ListAppointments = Depends(get_list_appointments)):
    return [
        AppointmentResponse.model_validate(appointment)
        for appointment in use_case.by_patient(patient_id)
    ]


@router.post("", status_code=201)
def create_appointment(payload: dict):
    """TODO: usar AutonomousAppointmentScheduling o ManualAppointmentScheduling según el rol."""
    return payload
