"""
Interfaz pública del módulo `patient` para el resto del monolito.

Los demás módulos consultan pacientes solo a través de esta clase, nunca leyendo
directamente las tablas del schema `patient`.
"""
from dataclasses import dataclass

from app.modules.patient.infrastructure.repository import PatientRepository


@dataclass(frozen=True)
class PatientSummary:
    patient_id: int
    full_name: str
    phone: str


class PatientDirectory:
    def __init__(self, repository: PatientRepository):
        self._repository = repository

    def find_summaries(self, patient_ids: set[int]) -> dict[int, PatientSummary]:
        return {
            patient.patient_id: PatientSummary(
                patient_id=patient.patient_id,
                full_name=patient.full_name,
                phone=patient.phone,
            )
            for patient in self._repository.find_by_ids(patient_ids)
        }

    def exists(self, patient_id: int) -> bool:
        return bool(self._repository.find_by_ids({patient_id}))

    def find_id_by_user(self, user_id: str) -> int | None:
        """Paciente asociado a una cuenta de acceso (identificador de Keycloak)."""
        patient = self._repository.find_by_user_id(user_id)
        return patient.patient_id if patient else None
