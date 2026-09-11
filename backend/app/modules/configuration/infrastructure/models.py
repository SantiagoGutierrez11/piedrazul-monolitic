"""Tablas del schema `configuration`."""
from datetime import time

from sqlalchemy import Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, module_table_args


class SystemParameterModel(Base):
    __tablename__ = "system_parameter"
    __table_args__ = module_table_args("configuration")

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="", nullable=False)


class DoctorScheduleModel(Base):
    __tablename__ = "doctor_schedule"
    __table_args__ = module_table_args(
        "configuration",
        UniqueConstraint("doctor_id", "day_of_week", name="uq_doctor_schedule_day"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
