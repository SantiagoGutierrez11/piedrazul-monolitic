"""Montado bajo /api/v1/medical (ver app/main.py)."""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.appointment.application.directory import AppointmentDirectory
from app.modules.appointment.infrastructure.repository import AppointmentRepository
from app.modules.configuration.application.directory import ConfigurationDirectory
from app.modules.configuration.infrastructure.repository import ConfigurationRepository
from app.modules.medical_staff.api.schemas import (
    AvailabilityResponse,
    AvailableDoctorResponse,
    CalendarResponse,
    DoctorResponse,
    WorkingHoursResponse,
)
from app.modules.medical_staff.application.availability import AvailabilityService
from app.modules.medical_staff.domain.factory.availability_generator import StandardGeneratorFactory
from app.modules.medical_staff.infrastructure.repository import DoctorRepository
from app.shared.clock import Clock, get_clock

# Todos los roles necesitan consultar profesionales y franjas disponibles.
router = APIRouter(dependencies=[Depends(get_current_user)])


def get_repository(db: Session = Depends(get_db)) -> DoctorRepository:
    return DoctorRepository(db)


def get_availability_service(
    db: Session = Depends(get_db), clock: Clock = Depends(get_clock)
) -> AvailabilityService:
    return AvailabilityService(
        schedules=ConfigurationDirectory(ConfigurationRepository(db)),
        occupancy=AppointmentDirectory(AppointmentRepository(db)),
        factory=StandardGeneratorFactory(),
        clock=clock,
    )


@router.get("/doctors", response_model=list[DoctorResponse])
def list_doctors(specialty: str | None = None, repository: DoctorRepository = Depends(get_repository)):
    doctors = repository.find_active_by_specialty(specialty) if specialty else repository.find_all_active()
    return [DoctorResponse.model_validate(doctor) for doctor in doctors]


@router.get("/doctors/available", response_model=list[AvailableDoctorResponse])
def list_available_doctors(
    specialty: str,
    repository: DoctorRepository = Depends(get_repository),
    availability: AvailabilityService = Depends(get_availability_service),
):
    """Profesionales activos de una especialidad, con su primera fecha con cupo."""
    return [
        AvailableDoctorResponse(
            doctor_id=doctor.doctor_id,
            full_name=doctor.full_name,
            specialty=doctor.specialty,
            next_available_date=availability.next_available_date(doctor.doctor_id),
        )
        for doctor in repository.find_active_by_specialty(specialty)
    ]


@router.get("/doctors/{doctor_id}/schedule", response_model=list[WorkingHoursResponse])
def get_doctor_schedule(doctor_id: int, db: Session = Depends(get_db)):
    hours = ConfigurationDirectory(ConfigurationRepository(db)).working_hours(doctor_id)
    return [WorkingHoursResponse.model_validate(item) for item in hours]


@router.get("/availability", response_model=AvailabilityResponse)
def get_availability(
    doctor_id: int,
    date: date,
    availability: AvailabilityService = Depends(get_availability_service),
):
    return AvailabilityResponse.from_day(doctor_id, availability.for_date(doctor_id, date))


@router.get("/availability/calendar", response_model=CalendarResponse)
def get_availability_calendar(
    doctor_id: int, availability: AvailabilityService = Depends(get_availability_service)
):
    return CalendarResponse.from_days(
        doctor_id, availability.last_bookable_date(), availability.calendar(doctor_id)
    )
