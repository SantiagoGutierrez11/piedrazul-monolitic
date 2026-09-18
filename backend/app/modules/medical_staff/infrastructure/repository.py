"""Acceso a datos del schema `medical_staff`."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.medical_staff.domain.entities import Doctor
from app.modules.medical_staff.infrastructure.models import DoctorModel


class DoctorRepository:
    def __init__(self, db: Session):
        self._db = db

    def find_all_active(self) -> list[Doctor]:
        rows = self._db.scalars(
            select(DoctorModel).where(DoctorModel.active.is_(True)).order_by(DoctorModel.full_name)
        ).all()
        return [self._to_entity(row) for row in rows]

    def find_by_id(self, doctor_id: int) -> Doctor | None:
        row = self._db.get(DoctorModel, doctor_id)
        return self._to_entity(row) if row else None

    def save(self, doctor: Doctor) -> Doctor:
        row = self._db.get(DoctorModel, doctor.doctor_id) if doctor.doctor_id else None
        if row is None:
            row = DoctorModel(doctor_id=doctor.doctor_id)
            self._db.add(row)

        row.full_name = doctor.full_name
        row.specialty = doctor.specialty
        row.active = doctor.active

        self._db.commit()
        self._db.refresh(row)
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: DoctorModel) -> Doctor:
        return Doctor(
            doctor_id=row.doctor_id,
            full_name=row.full_name,
            specialty=row.specialty,
            active=row.active,
        )
