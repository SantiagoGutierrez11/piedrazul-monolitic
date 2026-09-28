"""Acceso a las autorizaciones médicas del schema `appointment`."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.appointment.domain.entities import PatientAuthorization, ServiceType
from app.modules.appointment.infrastructure.models import PatientAuthorizationModel


class AuthorizationRepository:
    def __init__(self, db: Session):
        self._db = db

    def find_active(self, patient_id: int, now: datetime) -> PatientAuthorization | None:
        row = self._db.scalars(
            select(PatientAuthorizationModel)
            .where(
                PatientAuthorizationModel.patient_id == patient_id,
                PatientAuthorizationModel.used.is_(False),
                PatientAuthorizationModel.expires_at > now,
            )
            .order_by(PatientAuthorizationModel.authorized_at.desc())
        ).first()
        return self._to_entity(row) if row else None

    def save(self, authorization: PatientAuthorization) -> PatientAuthorization:
        row = (
            self._db.get(PatientAuthorizationModel, authorization.authorization_id)
            if authorization.authorization_id
            else None
        )
        if row is None:
            row = PatientAuthorizationModel()
            self._db.add(row)

        row.patient_id = authorization.patient_id
        row.service_type = authorization.service_type.value
        row.authorized_at = authorization.authorized_at
        row.expires_at = authorization.expires_at
        row.authorized_by_doctor_id = authorization.authorized_by_doctor_id
        row.appointment_id = authorization.appointment_id
        row.used = authorization.used

        self._db.commit()
        self._db.refresh(row)
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: PatientAuthorizationModel) -> PatientAuthorization:
        return PatientAuthorization(
            authorization_id=row.authorization_id,
            patient_id=row.patient_id,
            service_type=ServiceType(row.service_type),
            authorized_at=row.authorized_at,
            expires_at=row.expires_at,
            authorized_by_doctor_id=row.authorized_by_doctor_id,
            appointment_id=row.appointment_id,
            used=row.used,
        )
