from app.core.exceptions import NotFoundError, ValidationError
from app.modules.appointment.domain.entities import Appointment
from app.modules.appointment.domain.ports import DoctorLookup, PatientLookup
from app.modules.appointment.domain.validators.base import AppointmentValidator


class ExistenceValidator(AppointmentValidator):
    """El paciente debe existir y el profesional debe existir y estar activo."""

    def __init__(self, doctors: DoctorLookup, patients: PatientLookup):
        self._doctors = doctors
        self._patients = patients

    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        if not self._patients.exists(appointment.patient_id):
            raise NotFoundError("No se encontró el paciente de la cita.")

        doctor = self._doctors.find(appointment.doctor_id)
        if doctor is None:
            raise NotFoundError("No se encontró el profesional seleccionado.")
        if not doctor.active:
            raise ValidationError("El profesional seleccionado no está atendiendo en este momento.")
