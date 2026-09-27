"""
Interfaz pública del módulo `medical_staff` para el resto del monolito.

El módulo de citas valida al profesional (que exista, esté activo y preste el servicio) solo a
través de esta clase.
"""
from dataclasses import dataclass

from app.modules.medical_staff.infrastructure.repository import DoctorRepository


@dataclass(frozen=True)
class DoctorSummary:
    doctor_id: int
    full_name: str
    specialty: str
    active: bool


class DoctorDirectory:
    def __init__(self, repository: DoctorRepository):
        self._repository = repository

    def find(self, doctor_id: int) -> DoctorSummary | None:
        doctor = self._repository.find_by_id(doctor_id)
        if doctor is None:
            return None
        return DoctorSummary(
            doctor_id=doctor.doctor_id,
            full_name=doctor.full_name,
            specialty=doctor.specialty,
            active=doctor.active,
        )
