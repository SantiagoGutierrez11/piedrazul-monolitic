"""Montado bajo /api/v1/patients (ver app/main.py)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.security import CurrentUser, Role, require_role
from app.modules.identity.application.accounts import AccountDirectory
from app.modules.identity.domain.ports import IdentityProvider
from app.modules.identity.infrastructure.keycloak_provider import get_identity_provider
from app.modules.patient.api.schemas import (
    PatientProfileResponse,
    RegisterPatientRequest,
    RegisteredPatientResponse,
)
from app.modules.patient.application.register_patient import RegisterPatient
from app.modules.patient.infrastructure.repository import PatientRepository

router = APIRouter()


def get_register_patient(
    db: Session = Depends(get_db),
    provider: IdentityProvider = Depends(get_identity_provider),
) -> RegisterPatient:
    return RegisterPatient(PatientRepository(db), AccountDirectory(provider))


@router.post("/register", status_code=201, response_model=RegisteredPatientResponse)
def register(payload: RegisterPatientRequest, use_case: RegisterPatient = Depends(get_register_patient)):
    patient = use_case.execute(payload.to_registration())
    return RegisteredPatientResponse(
        patient_id=patient.patient_id, full_name=patient.full_name, email=patient.email
    )


@router.get("/count", dependencies=[Depends(require_role(Role.ADMINISTRADOR))])
def count_patients(db: Session = Depends(get_db)):
    return {"total": PatientRepository(db).count()}


@router.get("/me", response_model=PatientProfileResponse)
def get_me(
    user: CurrentUser = Depends(require_role(Role.PACIENTE)),
    db: Session = Depends(get_db),
):
    patient = PatientRepository(db).find_by_user_id(user.user_id)
    if patient is None:
        raise NotFoundError("No se encontró el perfil del paciente")
    return PatientProfileResponse.from_entity(patient)
