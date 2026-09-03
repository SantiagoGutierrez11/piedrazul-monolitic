"""Módulo de apoyo para registro/consulta de pacientes."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
def get_me():
    """TODO: resolver el paciente autenticado (ver core/security.py)."""
    return {}
