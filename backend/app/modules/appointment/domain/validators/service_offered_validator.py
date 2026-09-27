from app.core.exceptions import ValidationError
from app.modules.appointment.domain.entities import Appointment
from app.modules.appointment.domain.ports import DoctorLookup
from app.modules.appointment.domain.validators.base import AppointmentValidator


class ServiceOfferedValidator(AppointmentValidator):
    """El profesional debe pertenecer a la especialidad que presta el servicio solicitado."""

    def __init__(self, doctors: DoctorLookup):
        self._doctors = doctors

    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        doctor = self._doctors.find(appointment.doctor_id)
        if doctor is not None and doctor.specialty != appointment.service_type.specialty:
            raise ValidationError(
                f"{doctor.full_name} no presta el servicio de {appointment.service_type.label}."
            )
