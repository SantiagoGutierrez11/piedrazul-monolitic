"""Montado bajo /api/v1/configuration (ver app/main.py)."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/global")
def get_global_configuration():
    """TODO: usar ConfigurationService.get_appointment_window_weeks()."""
    return {"weeks": 4}


@router.put("/global/appointment-window")
def update_appointment_window(payload: dict):
    """TODO: usar ConfigurationService.update_appointment_window_weeks()."""
    return payload


@router.get("/doctor/{doctor_id}/schedule")
def get_doctor_schedule(doctor_id: int):
    """TODO: usar ConfigurationService.get_doctor_schedule()."""
    return []


@router.put("/doctor/{doctor_id}/schedule")
def update_doctor_schedule(doctor_id: int, payload: dict):
    """TODO: usar ConfigurationService.update_doctor_schedule()."""
    return payload
