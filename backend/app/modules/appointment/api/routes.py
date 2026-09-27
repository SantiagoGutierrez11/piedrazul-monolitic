"""
Rutas montadas bajo /api/v1/appointments (ver app/main.py). Cada handler delega en un
caso de uso de application/ — el router no debe contener lógica de negocio.
"""
from datetime import date, time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import DomainError, ValidationError
from app.core.security import Role, require_role
from app.modules.appointment.api.schemas import AppointmentResponse
from app.modules.appointment.application.list_appointments import ListAppointments
from app.modules.appointment.application.scheduling.autonomous_scheduling import (
    AutonomousAppointmentScheduling,
)
from app.modules.appointment.domain.entities import Appointment, AppointmentStatus, ServiceType
from app.modules.appointment.domain.validators.active_appointment_validator import (
    ActiveAppointmentValidator,
)
from app.modules.appointment.domain.validators.conflict_validator import ConflictValidator
from app.modules.appointment.domain.validators.data_appointment_validator import (
    DataAppointmentValidator,
)
from app.modules.appointment.infrastructure.repository import AppointmentRepository
from app.modules.patient.application.directory import PatientDirectory
from app.modules.patient.infrastructure.repository import PatientRepository

router = APIRouter()

STAFF = (Role.AGENDADOR, Role.MEDICO, Role.ADMINISTRADOR)


class ScheduleRequest(BaseModel):
    patient_id: int
    doctor_id: int
    doctor_name: str
    service_type: ServiceType
    date: date
    start_time: time
    end_time: time
    reason: str


def get_list_appointments(db: Session = Depends(get_db)) -> ListAppointments:
    return ListAppointments(
        AppointmentRepository(db), PatientDirectory(PatientRepository(db))
    )


@router.get(
    "/doctor/{doctor_id}/date/{date}",
    response_model=list[AppointmentResponse],
    dependencies=[Depends(require_role(*STAFF))],
)
def list_by_doctor_and_date(
    doctor_id: int,
    date: date,
    service_type: ServiceType | None = None,
    status: AppointmentStatus | None = None,
    use_case: ListAppointments = Depends(get_list_appointments),
):
    listing = use_case.by_doctor_and_date(doctor_id, date, service_type, status)
    return [AppointmentResponse.from_listing(item) for item in listing]


@router.get(
    "/patient/{patient_id}",
    response_model=list[AppointmentResponse],
    dependencies=[Depends(require_role(*STAFF))],
)
def list_by_patient(patient_id: int, use_case: ListAppointments = Depends(get_list_appointments)):
    return [AppointmentResponse.from_listing(item) for item in use_case.by_patient(patient_id)]


@router.post(
    "/autonomous",
    status_code=201,
    dependencies=[Depends(require_role(Role.PACIENTE, Role.AGENDADOR))],
)
def schedule_autonomous(dto: ScheduleRequest, db: Session = Depends(get_db)):
    appointment = Appointment(
        patient_id=dto.patient_id,
        doctor_id=dto.doctor_id,
        doctor_name=dto.doctor_name,
        service_type=dto.service_type,
        date=dto.date,
        start_time=dto.start_time,
        end_time=dto.end_time,
        reason=dto.reason,
    )

    # Cadena de validaciones (Strategy/Chain)
    validators = [
        DataAppointmentValidator(),
        ConflictValidator(),
        ActiveAppointmentValidator(max_active_appointments=2),
    ]

    use_case = AutonomousAppointmentScheduling(
        repository=AppointmentRepository(db), validators=validators
    )

    try:
        saved = use_case.execute(appointment)
        return {"message": "Cita agendada exitosamente", "appointment_id": saved.appointment_id}
    except (DomainError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
