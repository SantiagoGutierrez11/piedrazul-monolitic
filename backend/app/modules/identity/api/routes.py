"""Módulo de identidad. Por ahora queda como stub; el Corte 2 lo conecta a Keycloak/JWT."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    """TODO: implementar cuando se aborde autenticación (Corte 2)."""
    return {}
