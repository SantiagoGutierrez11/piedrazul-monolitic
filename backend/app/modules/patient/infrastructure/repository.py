"""Acceso a datos del schema `patient`."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.patient.domain.entities import Patient
from app.modules.patient.infrastructure.models import PatientModel


class PatientRepository:
    def __init__(self, db: Session):
        self._db = db

    def find_by_ids(self, patient_ids: set[int]) -> list[Patient]:
        if not patient_ids:
            return []
        rows = self._db.scalars(
            select(PatientModel).where(PatientModel.patient_id.in_(patient_ids))
        ).all()
        return [self._to_entity(row) for row in rows]

    def save(self, patient: Patient) -> Patient:
        row = self._db.get(PatientModel, patient.patient_id) if patient.patient_id else None
        if row is None:
            row = PatientModel(patient_id=patient.patient_id)
            self._db.add(row)

        row.first_name = patient.first_name
        row.last_name = patient.last_name
        row.phone = patient.phone

        self._db.commit()
        self._db.refresh(row)
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: PatientModel) -> Patient:
        return Patient(
            patient_id=row.patient_id,
            first_name=row.first_name,
            last_name=row.last_name,
            phone=row.phone,
        )
