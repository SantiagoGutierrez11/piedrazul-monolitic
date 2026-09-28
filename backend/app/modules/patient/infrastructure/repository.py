"""Acceso a datos del schema `patient`."""
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.modules.patient.domain.entities import DocumentType, Gender, Patient
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

    def count(self) -> int:
        return self._db.scalar(select(func.count()).select_from(PatientModel))

    def find_by_email(self, email: str) -> Patient | None:
        return self._first(select(PatientModel).where(PatientModel.email == email))

    def find_by_document(self, document_type: DocumentType, document_number: str) -> Patient | None:
        return self._first(
            select(PatientModel).where(
                PatientModel.document_type == document_type.value,
                PatientModel.document_number == document_number,
            )
        )

    def find_by_user_id(self, user_id: str) -> Patient | None:
        return self._first(select(PatientModel).where(PatientModel.user_id == user_id))

    def save(self, patient: Patient) -> Patient:
        row = self._db.get(PatientModel, patient.patient_id) if patient.patient_id else None
        if row is None:
            row = PatientModel(patient_id=patient.patient_id)
            self._db.add(row)

        row.first_name = patient.first_name
        row.middle_name = patient.middle_name
        row.last_name = patient.last_name
        row.second_last_name = patient.second_last_name
        row.phone = patient.phone
        row.email = patient.email
        row.birth_date = patient.birth_date
        row.gender = patient.gender.value if patient.gender else None
        row.document_type = patient.document_type.value if patient.document_type else None
        row.document_number = patient.document_number
        row.user_id = patient.user_id

        try:
            self._db.commit()
        except IntegrityError as exc:
            # Dos registros simultáneos con el mismo correo o documento: gana el primero.
            self._db.rollback()
            raise ConflictError("Ya existe un paciente registrado con ese correo o documento") from exc
        self._db.refresh(row)
        return self._to_entity(row)

    def _first(self, statement) -> Patient | None:
        row = self._db.scalars(statement).first()
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(row: PatientModel) -> Patient:
        return Patient(
            patient_id=row.patient_id,
            first_name=row.first_name,
            middle_name=row.middle_name,
            last_name=row.last_name,
            second_last_name=row.second_last_name,
            phone=row.phone,
            email=row.email,
            birth_date=row.birth_date,
            gender=Gender(row.gender) if row.gender else None,
            document_type=DocumentType(row.document_type) if row.document_type else None,
            document_number=row.document_number,
            user_id=row.user_id,
        )
