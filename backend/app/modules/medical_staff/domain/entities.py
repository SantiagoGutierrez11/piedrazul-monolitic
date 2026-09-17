"""Entidades del personal médico."""
from dataclasses import dataclass


@dataclass
class Doctor:
    doctor_id: int
    full_name: str
    specialty: str
    active: bool = True
