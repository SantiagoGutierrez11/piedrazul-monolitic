"""Acceso a datos del schema `configuration`."""
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.configuration.domain.entities import DoctorScheduleConfiguration, SystemParameter
from app.modules.configuration.infrastructure.models import DoctorScheduleModel, SystemParameterModel


class ConfigurationRepository:
    def __init__(self, db: Session):
        self._db = db

    def find_parameter(self, key: str) -> SystemParameter | None:
        row = self._db.get(SystemParameterModel, key)
        if row is None:
            return None
        return SystemParameter(key=row.key, value=row.value, description=row.description)

    def save_parameter(self, parameter: SystemParameter) -> SystemParameter:
        row = self._db.get(SystemParameterModel, parameter.key)
        if row is None:
            row = SystemParameterModel(key=parameter.key)
            self._db.add(row)
        row.value = parameter.value
        row.description = parameter.description
        self._db.commit()
        return parameter

    def find_schedule_by_doctor(self, doctor_id: int) -> list[DoctorScheduleConfiguration]:
        rows = self._db.scalars(
            select(DoctorScheduleModel)
            .where(DoctorScheduleModel.doctor_id == doctor_id)
            .order_by(DoctorScheduleModel.day_of_week)
        ).all()
        return [self._to_entity(row) for row in rows]

    def replace_schedule(
        self, doctor_id: int, schedules: list[DoctorScheduleConfiguration]
    ) -> list[DoctorScheduleConfiguration]:
        """El horario de un profesional se reemplaza completo: el formulario envía la semana entera."""
        self._db.execute(delete(DoctorScheduleModel).where(DoctorScheduleModel.doctor_id == doctor_id))
        self._db.add_all(
            DoctorScheduleModel(
                doctor_id=doctor_id,
                day_of_week=schedule.day_of_week,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                interval_minutes=schedule.interval_minutes,
            )
            for schedule in schedules
        )
        self._db.commit()
        return self.find_schedule_by_doctor(doctor_id)

    @staticmethod
    def _to_entity(row: DoctorScheduleModel) -> DoctorScheduleConfiguration:
        return DoctorScheduleConfiguration(
            doctor_id=row.doctor_id,
            day_of_week=row.day_of_week,
            start_time=row.start_time,
            end_time=row.end_time,
            interval_minutes=row.interval_minutes,
            id=row.id,
        )
