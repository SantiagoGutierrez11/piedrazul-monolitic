"""DTOs del módulo de pacientes."""
import re
from datetime import date

from pydantic import Field, field_validator, model_validator

from app.modules.patient.application.register_patient import PatientRegistration
from app.modules.patient.domain.entities import DocumentType, Gender, Patient
from app.shared.schemas import CamelModel

NAME_PATTERN = r"^[A-Za-zÀ-ÿ' -]*$"
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PHONE_PATTERN = re.compile(r"^\+?\d{7,15}$")


class RegisterPatientRequest(CamelModel):
    first_name: str = Field(min_length=2, max_length=80, pattern=NAME_PATTERN)
    middle_name: str = Field(default="", max_length=80, pattern=NAME_PATTERN)
    last_name: str = Field(min_length=2, max_length=80, pattern=NAME_PATTERN)
    second_last_name: str = Field(default="", max_length=80, pattern=NAME_PATTERN)
    email: str = Field(max_length=120, pattern=EMAIL_PATTERN)
    phone: str
    birth_date: date
    gender: Gender
    document_type: DocumentType
    document_number: str = Field(pattern=r"^[A-Za-z0-9]{5,15}$")
    password: str = Field(min_length=8, max_length=64)
    confirm_password: str

    @field_validator("first_name", "middle_name", "last_name", "second_last_name", "email", mode="before")
    @classmethod
    def _strip(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("phone")
    @classmethod
    def _normalize_phone(cls, value: str) -> str:
        phone = re.sub(r"[\s-]", "", value)
        if not PHONE_PATTERN.match(phone):
            raise ValueError("El teléfono debe tener entre 7 y 15 dígitos")
        return phone

    @model_validator(mode="after")
    def _passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        return self

    def to_registration(self) -> PatientRegistration:
        return PatientRegistration(
            first_name=self.first_name,
            middle_name=self.middle_name,
            last_name=self.last_name,
            second_last_name=self.second_last_name,
            email=self.email,
            phone=self.phone,
            birth_date=self.birth_date,
            gender=self.gender,
            document_type=self.document_type,
            document_number=self.document_number,
            password=self.password,
        )


class RegisteredPatientResponse(CamelModel):
    patient_id: int
    full_name: str
    email: str


class PatientProfileResponse(CamelModel):
    patient_id: int
    full_name: str
    first_name: str
    middle_name: str
    last_name: str
    second_last_name: str
    email: str | None
    phone: str
    birth_date: date | None
    gender: Gender | None
    document_type: DocumentType | None
    document_number: str | None

    @classmethod
    def from_entity(cls, patient: Patient) -> "PatientProfileResponse":
        return cls(
            patient_id=patient.patient_id,
            full_name=patient.full_name,
            first_name=patient.first_name,
            middle_name=patient.middle_name,
            last_name=patient.last_name,
            second_last_name=patient.second_last_name,
            email=patient.email,
            phone=patient.phone,
            birth_date=patient.birth_date,
            gender=patient.gender,
            document_type=patient.document_type,
            document_number=patient.document_number,
        )
