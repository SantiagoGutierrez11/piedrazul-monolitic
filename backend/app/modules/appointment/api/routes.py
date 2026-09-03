"""
Rutas montadas bajo /api/v1/appointments (ver app/main.py). Cada handler delega en un
caso de uso de application/ — el router no debe contener lógica de negocio.
"""
from datetime import date

from fastapi import APIRouter

router = APIRouter()


@router.get("/doctor/{doctor_id}/date/{date}")
def list_by_doctor_and_date(doctor_id: int, date: date):
    """TODO: inyectar el caso de uso y devolver el listado real."""
    return []


@router.post("", status_code=201)
def create_appointment(payload: dict):
    """TODO: usar AutonomousAppointmentScheduling o ManualAppointmentScheduling según el rol."""
    return payload
