"""Acceso a datos del schema `appointment`."""
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.modules.appointment.domain.entities import (
    ACTIVE_STATUSES,
    Appointment,
    AppointmentStatus,
    ServiceType,
)
from app.modules.appointment.infrastructure.models import AppointmentModel


class AppointmentRepository:
    def __init__(self, db: Session):
        self._db = db

    def find_by_doctor_and_date(self, doctor_id: int, on_date: date) -> list[Appointment]:
        rows = self._db.scalars(
            select(AppointmentModel)
            .where(AppointmentModel.doctor_id == doctor_id, AppointmentModel.date == on_date)
            .order_by(AppointmentModel.start_time)
        ).all()
        return [self._to_entity(row) for row in rows]

    def find_between(self, date_from: date, date_to: date) -> list[Appointment]:
        rows = self._db.scalars(
            select(AppointmentModel)
            .where(AppointmentModel.date >= date_from, AppointmentModel.date <= date_to)
            .order_by(AppointmentModel.date, AppointmentModel.start_time)
        ).all()
        return [self._to_entity(row) for row in rows]

    def count_active_from(self, from_date: date) -> int:
        return self._db.scalar(
            select(func.count())
            .select_from(AppointmentModel)
            .where(
                AppointmentModel.date >= from_date,
                AppointmentModel.status.in_([status.value for status in ACTIVE_STATUSES]),
            )
        )

    def find_by_id(self, appointment_id: int) -> Appointment | None:
        row = self._db.get(AppointmentModel, appointment_id)
        return self._to_entity(row) if row else None

    def find_by_patient(self, patient_id: int) -> list[Appointment]:
        rows = self._db.scalars(
            select(AppointmentModel)
            .where(AppointmentModel.patient_id == patient_id)
            .order_by(AppointmentModel.date.desc(), AppointmentModel.start_time)
        ).all()
        return [self._to_entity(row) for row in rows]

    def find_active_by_patient(self, patient_id: int, from_date: date) -> list[Appointment]:
        rows = self._db.scalars(
            select(AppointmentModel)
            .where(
                AppointmentModel.patient_id == patient_id,
                AppointmentModel.date >= from_date,
                AppointmentModel.status.in_([status.value for status in ACTIVE_STATUSES]),
            )
            .order_by(AppointmentModel.date, AppointmentModel.start_time)
        ).all()
        return [self._to_entity(row) for row in rows]

    def find_by_doctor_between(self, doctor_id: int, date_from: date, date_to: date) -> list[Appointment]:
        rows = self._db.scalars(
            select(AppointmentModel).where(
                AppointmentModel.doctor_id == doctor_id,
                AppointmentModel.date >= date_from,
                AppointmentModel.date <= date_to,
            )
        ).all()
        return [self._to_entity(row) for row in rows]

    def save(self, appointment: Appointment) -> Appointment:
        row = (
            self._db.get(AppointmentModel, appointment.appointment_id)
            if appointment.appointment_id
            else None
        )
        if row is None:
            row = AppointmentModel()
            self._db.add(row)

        row.patient_id = appointment.patient_id
        row.doctor_id = appointment.doctor_id
        row.doctor_name = appointment.doctor_name
        row.service_type = appointment.service_type.value
        row.date = appointment.date
        row.start_time = appointment.start_time
        row.end_time = appointment.end_time
        row.reason = appointment.reason
        row.notes = appointment.notes
        row.status = appointment.status.value

        try:
            self._db.commit()
        except IntegrityError as exc:
            # Otra persona confirmó la misma franja justo antes (ver Vista de Procesos).
            self._db.rollback()
            raise ConflictError("Ese horario ya no está disponible. Por favor elige otro.") from exc
        self._db.refresh(row)
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: AppointmentModel) -> Appointment:
        return Appointment(
            appointment_id=row.appointment_id,
            patient_id=row.patient_id,
            doctor_id=row.doctor_id,
            doctor_name=row.doctor_name,
            service_type=ServiceType(row.service_type),
            date=row.date,
            start_time=row.start_time,
            end_time=row.end_time,
            reason=row.reason,
            notes=row.notes,
            status=AppointmentStatus(row.status),
        )
