"""Montado bajo /api/v1/configuration (ver app/main.py)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import Role, get_current_user, require_role
from app.modules.configuration.api.schemas import (
    AppointmentWindowRequest,
    DoctorScheduleItem,
    DoctorScheduleRequest,
    GlobalConfigurationResponse,
)
from app.modules.configuration.application.service import ConfigurationService
from app.modules.configuration.domain.entities import DoctorScheduleConfiguration
from app.modules.configuration.infrastructure.repository import ConfigurationRepository

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> ConfigurationService:
    return ConfigurationService(ConfigurationRepository(db))


@router.get(
    "/global",
    response_model=GlobalConfigurationResponse,
    dependencies=[Depends(get_current_user)],
)
def get_global_configuration(service: ConfigurationService = Depends(get_service)):
    return GlobalConfigurationResponse(weeks=service.get_appointment_window_weeks())


@router.put(
    "/global/appointment-window",
    response_model=GlobalConfigurationResponse,
    dependencies=[Depends(require_role(Role.ADMINISTRADOR))],
)
def update_appointment_window(
    payload: AppointmentWindowRequest, service: ConfigurationService = Depends(get_service)
):
    return GlobalConfigurationResponse(weeks=service.update_appointment_window_weeks(payload.weeks))


@router.get(
    "/doctor/{doctor_id}/schedule",
    response_model=list[DoctorScheduleItem],
    dependencies=[Depends(get_current_user)],
)
def get_doctor_schedule(doctor_id: int, service: ConfigurationService = Depends(get_service)):
    return [DoctorScheduleItem.model_validate(item) for item in service.get_doctor_schedule(doctor_id)]


@router.put(
    "/doctor/{doctor_id}/schedule",
    response_model=list[DoctorScheduleItem],
    dependencies=[Depends(require_role(Role.ADMINISTRADOR))],
)
def update_doctor_schedule(
    doctor_id: int,
    payload: DoctorScheduleRequest,
    service: ConfigurationService = Depends(get_service),
):
    schedules = [
        DoctorScheduleConfiguration(
            doctor_id=doctor_id,
            day_of_week=item.day_of_week,
            start_time=item.start_time,
            end_time=item.end_time,
            interval_minutes=item.interval_minutes,
        )
        for item in payload.schedules
    ]
    saved = service.update_doctor_schedule(doctor_id, schedules)
    return [DoctorScheduleItem.model_validate(item) for item in saved]
