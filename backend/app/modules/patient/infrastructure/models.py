"""Tablas del schema `patient`."""
from datetime import date

from sqlalchemy import Date, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, module_table_args


class PatientModel(Base):
    __tablename__ = "patient"
    __table_args__ = module_table_args(
        "patient",
        UniqueConstraint("document_type", "document_number", name="uq_patient_document"),
    )

    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    second_last_name: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    email: Mapped[str | None] = mapped_column(String(120), unique=True)
    birth_date: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(20))
    document_type: Mapped[str | None] = mapped_column(String(10))
    document_number: Mapped[str | None] = mapped_column(String(20))
    user_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
