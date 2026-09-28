"""Tablas del schema `medical_staff`."""
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, module_table_args


class DoctorModel(Base):
    __tablename__ = "doctor"
    __table_args__ = module_table_args("medical_staff")

    doctor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    specialty: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    user_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
