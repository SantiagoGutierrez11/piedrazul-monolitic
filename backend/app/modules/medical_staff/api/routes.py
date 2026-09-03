"""Módulo de apoyo consumido por el agendamiento (disponibilidad) y el listado de citas
(selector de médico). Relacionado con `configuration` para los horarios por profesional.
"""
from datetime import date

from fastapi import APIRouter

router = APIRouter()


@router.get("/doctors")
def list_doctors():
    """TODO: listar médicos activos."""
    return []


@router.get("/doctors/{doctor_id}/schedule")
def get_doctor_schedule(doctor_id: int):
    """TODO: delegar a app.modules.configuration (horario configurado del profesional)."""
    return []


@router.get("/availability")
def get_availability(doctor_id: int, date: date):
    """TODO: usar get_availability_generator() de domain/factory/availability_generator.py."""
    return []
