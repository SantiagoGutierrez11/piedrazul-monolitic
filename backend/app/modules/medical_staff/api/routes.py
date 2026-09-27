from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.appointment.infrastructure.repository import AppointmentRepository
from app.modules.medical_staff.api.schemas import DoctorResponse
from app.modules.medical_staff.domain.factory.availability_generator import get_availability_generator
from app.modules.medical_staff.infrastructure.repository import DoctorRepository

router = APIRouter()


def get_repository(db: Session = Depends(get_db)) -> DoctorRepository:
    return DoctorRepository(db)


@router.get("/doctors", response_model=list[DoctorResponse])
def list_doctors(repository: DoctorRepository = Depends(get_repository)):
    return [DoctorResponse.model_validate(doctor) for doctor in repository.find_all_active()]


@router.get("/doctors/{doctor_id}/schedule")
def get_doctor_schedule(doctor_id: int):
    """TODO: delegar a app.modules.configuration (horario configurado del profesional)."""
    return []


@router.get("/availability")
def get_availability(doctor_id: int, date: date, db: Session = Depends(get_db)):
    generator = get_availability_generator(AppointmentRepository(db))
    slots = generator.generate(doctor_id=doctor_id, on_date=date)
    return {
        "doctor_id": doctor_id,
        "date": date,
        "available_slots": [s.strftime("%H:%M") for s in slots],
    }
