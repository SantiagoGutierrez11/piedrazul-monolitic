"""Datos mínimos de un centro médico para las pruebas del agendamiento."""
from datetime import date, datetime, time

from app.modules.appointment.domain.entities import (
    Appointment,
    AppointmentStatus,
    PatientAuthorization,
    ServiceType,
)
from app.modules.appointment.infrastructure.authorization_repository import AuthorizationRepository
from app.modules.appointment.infrastructure.repository import AppointmentRepository
from app.modules.configuration.domain.entities import DoctorScheduleConfiguration
from app.modules.configuration.infrastructure.repository import ConfigurationRepository
from app.modules.medical_staff.domain.entities import Doctor
from app.modules.medical_staff.infrastructure.repository import DoctorRepository
from app.modules.patient.domain.entities import Patient
from app.modules.patient.infrastructure.repository import PatientRepository

MARIA_USER, CARLOS_USER = "kc-maria", "kc-carlos"
MARIA_ID, CARLOS_ID = 1, 2
GENERAL, PHYSIO, CHIRO = 1, 2, 3  # profesionales


def create_clinic(db) -> None:
    """Tres profesionales (el de Quiropraxia sin horario) y dos pacientes con cuenta."""
    doctors = DoctorRepository(db)
    doctors.save(Doctor(doctor_id=GENERAL, full_name="Dra. Laura Muñoz", specialty="Medicina General"))
    doctors.save(Doctor(doctor_id=PHYSIO, full_name="Dr. Juan Pérez", specialty="Fisioterapia"))
    doctors.save(Doctor(doctor_id=CHIRO, full_name="Dra. Ana Soto", specialty="Quiropraxia"))

    configuration = ConfigurationRepository(db)
    for doctor_id in (GENERAL, PHYSIO):
        configuration.replace_schedule(
            doctor_id,
            [
                DoctorScheduleConfiguration(
                    doctor_id=doctor_id, day_of_week=day, start_time=time(8, 0), end_time=time(12, 0), interval_minutes=30
                )
                for day in range(1, 6)
            ],
        )

    patients = PatientRepository(db)
    patients.save(Patient(patient_id=MARIA_ID, first_name="María", last_name="García", phone="3001234567", user_id=MARIA_USER))
    patients.save(Patient(patient_id=CARLOS_ID, first_name="Carlos", last_name="Rodríguez", phone="3109876543", user_id=CARLOS_USER))


def book(db, patient_id: int, doctor_id: int, on_date: date, start: time, status=AppointmentStatus.AGENDADA) -> Appointment:
    """Registra una cita directamente, sin pasar por las validaciones."""
    return AppointmentRepository(db).save(
        Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            doctor_name="Profesional",
            service_type=ServiceType.CONSULTA_GENERAL,
            date=on_date,
            start_time=start,
            end_time=time(start.hour, start.minute + 30) if start.minute < 30 else time(start.hour + 1, 0),
            reason="Control general",
            status=status,
        )
    )


def authorize(db, patient_id: int, service: ServiceType, granted_at: datetime = datetime(2026, 3, 2, 9, 30)):
    attended = book(db, patient_id, GENERAL, granted_at.date(), time(9, 0), AppointmentStatus.ATENDIDA)
    return AuthorizationRepository(db).save(PatientAuthorization.grant(attended, service, granted_at))
