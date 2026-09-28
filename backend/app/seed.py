"""
Carga datos de ejemplo para poder probar el listado de citas y la configuración.

Uso: python -m app.seed
"""
from datetime import date, datetime, time, timedelta

from sqlalchemy import text

from app.core.database import SessionLocal, init_db
from app.modules.appointment.domain.entities import (
    Appointment,
    AppointmentStatus,
    PatientAuthorization,
    ServiceType,
)
from app.modules.appointment.infrastructure.authorization_repository import AuthorizationRepository
from app.modules.appointment.infrastructure.repository import AppointmentRepository
from app.modules.configuration.application.service import ConfigurationService
from app.modules.configuration.domain.entities import DoctorScheduleConfiguration
from app.modules.configuration.infrastructure.repository import ConfigurationRepository
from app.modules.medical_staff.domain.entities import Doctor
from app.modules.medical_staff.infrastructure.repository import DoctorRepository
from app.modules.patient.domain.entities import Patient
from app.modules.patient.infrastructure.repository import PatientRepository
from app.shared.clock import SystemClock
from app.shared.holidays import ColombianHolidays

# Cuenta medico@piedrazul.com del realm de Keycloak.
DEMO_DOCTOR_USER_ID = "9c4a7e36-1d2b-4e8f-a5c3-7f6e8d2b4a03"

DOCTORS = [
    Doctor(
        doctor_id=1,
        full_name="Dra. Laura Muñoz",
        specialty="Medicina General",
        user_id=DEMO_DOCTOR_USER_ID,
    ),
    Doctor(doctor_id=2, full_name="Dr. Juan Pérez", specialty="Fisioterapia"),
    Doctor(doctor_id=3, full_name="Dra. Ana Soto", specialty="Quiropraxia"),
]

# Cuenta paciente@piedrazul.com del realm de Keycloak (keycloak/realm-piedrazul.json).
DEMO_PATIENT_USER_ID = "d2f6b958-6c4e-4a17-b3d9-8a1c5e7f2b04"
DEMO_PATIENT_ID = 1

PATIENTS = [
    Patient(
        patient_id=1,
        first_name="María",
        last_name="García",
        second_last_name="López",
        phone="+57 300 123 4567",
        email="paciente@piedrazul.com",
        user_id=DEMO_PATIENT_USER_ID,
    ),
    Patient(patient_id=2, first_name="Carlos", last_name="Rodríguez", phone="+57 310 987 6543"),
    Patient(patient_id=3, first_name="Laura", last_name="Sánchez", phone="+57 320 456 7890"),
    Patient(patient_id=4, first_name="Roberto", last_name="Díaz", phone="+57 301 222 3344"),
    Patient(patient_id=5, first_name="Ana", last_name="Martínez", phone="+57 315 555 1122"),
    Patient(patient_id=6, first_name="Jorge", last_name="Ramírez", phone="+57 312 777 8899"),
    Patient(patient_id=7, first_name="Sofía", last_name="Torres", phone="+57 318 444 5566"),
    Patient(patient_id=8, first_name="Andrés", last_name="Gómez", phone="+57 305 666 7788"),
    Patient(patient_id=9, first_name="Valentina", last_name="Castro", phone="+57 317 999 0011"),
    Patient(patient_id=10, first_name="Diego", last_name="Herrera", phone="+57 316 333 2211"),
]

SERVICES = [
    (time(8, 0), time(8, 30), ServiceType.CONSULTA_GENERAL, "Control general", AppointmentStatus.AGENDADA),
    (time(9, 0), time(9, 30), ServiceType.FISIOTERAPIA, "Terapia de rodilla", AppointmentStatus.AGENDADA),
    (time(10, 0), time(10, 30), ServiceType.QUIROPRAXIA, "Dolor lumbar", AppointmentStatus.CANCELADA),
]


def _appointments(doctor: Doctor, on_date: date) -> list[Appointment]:
    """Cada profesional atiende a tres pacientes distintos en la misma jornada.

    La paciente de prueba (María) queda sin citas activas para poder recorrer el agendamiento.
    """
    primer_paciente = 1 + (doctor.doctor_id - 1) * len(SERVICES)
    return [
        Appointment(
            patient_id=PATIENTS[primer_paciente + indice].patient_id,
            doctor_id=doctor.doctor_id,
            doctor_name=doctor.full_name,
            service_type=servicio,
            date=on_date,
            start_time=inicio,
            end_time=fin,
            reason=motivo,
            status=estado,
        )
        for indice, (inicio, fin, servicio, motivo, estado) in enumerate(SERVICES)
    ]


def _sync_patient_sequence(db) -> None:
    """Los pacientes de ejemplo se insertan con id fijo; en PostgreSQL la secuencia debe
    avanzar para que los pacientes que se registren después no choquen con esos ids."""
    if db.get_bind().dialect.name != "postgresql":
        return
    db.execute(
        text(
            "SELECT setval(pg_get_serial_sequence('patient.patient', 'patient_id'), "
            "(SELECT MAX(patient_id) FROM patient.patient))"
        )
    )
    db.commit()


def _previous_business_day(day: date) -> date:
    holidays = ColombianHolidays()
    while day.weekday() >= 5 or holidays.is_holiday(day):
        day -= timedelta(days=1)
    return day


def _demo_patient_history(citas: AppointmentRepository, autorizaciones: AuthorizationRepository, hoy: date) -> None:
    """Historial de María: una consulta cancelada y otra atendida en la que la médica la
    autorizó para Fisioterapia, así el agendamiento muestra un servicio especializado habilitado."""
    if citas.find_by_patient(DEMO_PATIENT_ID):
        return
    doctora = DOCTORS[0]
    cancelada = _previous_business_day(hoy - timedelta(days=25))
    atendida = _previous_business_day(hoy - timedelta(days=10))
    historial = [
        (cancelada, time(10, 0), AppointmentStatus.CANCELADA),
        (atendida, time(9, 0), AppointmentStatus.ATENDIDA),
    ]
    for dia, inicio, estado in historial:
        cita = citas.save(
            Appointment(
                patient_id=DEMO_PATIENT_ID,
                doctor_id=doctora.doctor_id,
                doctor_name=doctora.full_name,
                service_type=ServiceType.CONSULTA_GENERAL,
                date=dia,
                start_time=inicio,
                end_time=time(inicio.hour, 30),
                reason="Control general",
                status=estado,
            )
        )
    autorizaciones.save(
        PatientAuthorization.grant(cita, ServiceType.FISIOTERAPIA, datetime.combine(atendida, time(9, 30)))
    )


def run() -> None:
    init_db()
    db = SessionLocal()
    try:
        doctores = DoctorRepository(db)
        for doctor in DOCTORS:
            doctores.save(doctor)

        pacientes = PatientRepository(db)
        for paciente in PATIENTS:
            pacientes.save(paciente)
        _sync_patient_sequence(db)

        configuracion = ConfigurationService(ConfigurationRepository(db))
        configuracion.update_appointment_window_weeks(4)
        for doctor in DOCTORS:
            configuracion.update_doctor_schedule(
                doctor.doctor_id,
                [
                    DoctorScheduleConfiguration(
                        doctor_id=doctor.doctor_id,
                        day_of_week=dia,
                        start_time=time(8, 0),
                        end_time=time(12, 0),
                        interval_minutes=30,
                    )
                    for dia in range(1, 6)
                ],
            )

        citas = AppointmentRepository(db)
        hoy = SystemClock().now().date()
        _demo_patient_history(citas, AuthorizationRepository(db), hoy)
        for on_date in (hoy, hoy + timedelta(days=1)):
            for doctor in DOCTORS:
                if citas.find_by_doctor_and_date(doctor.doctor_id, on_date):
                    continue
                for cita in _appointments(doctor, on_date):
                    citas.save(cita)

        print(
            f"Datos de ejemplo cargados: {len(DOCTORS)} profesionales, {len(PATIENTS)} pacientes "
            f"y citas para {hoy} y {hoy + timedelta(days=1)}."
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
