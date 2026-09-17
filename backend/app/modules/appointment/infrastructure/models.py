"""Tablas del schema `appointment`."""
from datetime import date as date_type, time

from sqlalchemy import Date, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, module_table_args


class AppointmentModel(Base):
    __tablename__ = "appointment"
    # Esta restricción es la que evita la doble reserva cuando dos agendadores
    # confirman el mismo horario a la vez (ver Vista de Procesos del taller).
    __table_args__ = module_table_args(
        "appointment",
        UniqueConstraint("doctor_id", "date", "start_time", name="uq_appointment_doctor_slot"),
    )

    appointment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    doctor_name: Mapped[str] = mapped_column(String(120), nullable=False)
    service_type: Mapped[str] = mapped_column(String(40), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
