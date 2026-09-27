"""Tablas del schema `patient`."""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, module_table_args


class PatientModel(Base):
    __tablename__ = "patient"
    __table_args__ = module_table_args("patient")

    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False, default="")
