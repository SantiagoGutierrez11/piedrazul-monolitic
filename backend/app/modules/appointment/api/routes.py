"""
Rutas montadas bajo /api/v1/appointments (ver app/main.py). Cada handler delega en un
caso de uso de application/ — el router no debe contener lógica de negocio.
"""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.security import CurrentUser, Role, require_role
from app.modules.appointment.api.schemas import (
    AppointmentResponse,
    AttendRequest,
    PatientBookingRequest,
    SchedulingOptionsResponse,
)
from app.modules.appointment.application.appointment_status import (
    AttendAppointment,
    CancelPatientAppointment,
)
from app.modules.appointment.application.list_appointments import ListAppointments
from app.modules.appointment.application.scheduling.patient_scheduling import (
    SchedulePatientAppointment,
)
from app.modules.appointment.application.scheduling_options import SchedulingOptionsQuery
from app.modules.appointment.domain.entities import AppointmentStatus, ServiceType
from app.modules.appointment.infrastructure.authorization_repository import AuthorizationRepository
from app.modules.appointment.infrastructure.repository import AppointmentRepository
from app.modules.configuration.application.directory import ConfigurationDirectory
from app.modules.configuration.infrastructure.repository import ConfigurationRepository
from app.modules.medical_staff.application.directory import DoctorDirectory
from app.modules.medical_staff.infrastructure.repository import DoctorRepository
from app.modules.patient.application.directory import PatientDirectory
from app.modules.patient.infrastructure.repository import PatientRepository
from app.shared.clock import Clock, get_clock

router = APIRouter()

STAFF = (Role.AGENDADOR, Role.MEDICO, Role.ADMINISTRADOR)
current_patient_user = require_role(Role.PACIENTE)


def get_list_appointments(db: Session = Depends(get_db)) -> ListAppointments:
    return ListAppointments(
        AppointmentRepository(db), PatientDirectory(PatientRepository(db))
    )


def get_schedule_patient_appointment(
    db: Session = Depends(get_db), clock: Clock = Depends(get_clock)
) -> SchedulePatientAppointment:
    return SchedulePatientAppointment(
        repository=AppointmentRepository(db),
        patients=PatientDirectory(PatientRepository(db)),
        doctors=DoctorDirectory(DoctorRepository(db)),
        schedules=ConfigurationDirectory(ConfigurationRepository(db)),
        authorizations=AuthorizationRepository(db),
        clock=clock,
    )


def get_scheduling_options(
    db: Session = Depends(get_db), clock: Clock = Depends(get_clock)
) -> SchedulingOptionsQuery:
    return SchedulingOptionsQuery(
        appointments=AppointmentRepository(db),
        patients=PatientDirectory(PatientRepository(db)),
        schedules=ConfigurationDirectory(ConfigurationRepository(db)),
        authorizations=AuthorizationRepository(db),
        clock=clock,
    )


# ---------------------------------------------------------------- Personal del centro


@router.get(
    "/doctor/{doctor_id}/date/{date}",
    response_model=list[AppointmentResponse],
    dependencies=[Depends(require_role(*STAFF))],
)
def list_by_doctor_and_date(
    doctor_id: int,
    date: date,
    service_type: ServiceType | None = None,
    status: AppointmentStatus | None = None,
    use_case: ListAppointments = Depends(get_list_appointments),
):
    listing = use_case.by_doctor_and_date(doctor_id, date, service_type, status)
    return [AppointmentResponse.from_listing(item) for item in listing]


@router.get(
    "/patient/{patient_id}",
    response_model=list[AppointmentResponse],
    dependencies=[Depends(require_role(*STAFF))],
)
def list_by_patient(patient_id: int, use_case: ListAppointments = Depends(get_list_appointments)):
    return [AppointmentResponse.from_listing(item) for item in use_case.by_patient(patient_id)]


@router.patch(
    "/{appointment_id}/attend",
    response_model=AppointmentResponse,
    dependencies=[Depends(require_role(Role.MEDICO))],
)
def attend(
    appointment_id: int,
    payload: AttendRequest | None = None,
    db: Session = Depends(get_db),
    clock: Clock = Depends(get_clock),
):
    use_case = AttendAppointment(AppointmentRepository(db), AuthorizationRepository(db), clock)
    authorized = payload.authorized_service_type if payload else None
    return AppointmentResponse.from_appointment(use_case.execute(appointment_id, authorized))


# ---------------------------------------------------------------- Paciente (agendamiento autónomo)


@router.get("/me", response_model=list[AppointmentResponse])
def my_appointments(
    user: CurrentUser = Depends(current_patient_user),
    db: Session = Depends(get_db),
    use_case: ListAppointments = Depends(get_list_appointments),
):
    patient_id = PatientDirectory(PatientRepository(db)).find_id_by_user(user.user_id)
    if patient_id is None:
        raise NotFoundError("No se encontró el perfil del paciente")
    return [AppointmentResponse.from_listing(item) for item in use_case.by_patient(patient_id)]


@router.get("/me/options", response_model=SchedulingOptionsResponse)
def my_scheduling_options(
    user: CurrentUser = Depends(current_patient_user),
    query: SchedulingOptionsQuery = Depends(get_scheduling_options),
):
    return SchedulingOptionsResponse.from_options(query.for_user(user.user_id))


@router.post("/autonomous", status_code=201, response_model=AppointmentResponse)
def schedule_autonomous(
    payload: PatientBookingRequest,
    user: CurrentUser = Depends(current_patient_user),
    use_case: SchedulePatientAppointment = Depends(get_schedule_patient_appointment),
):
    # El paciente siempre agenda para sí mismo: su identidad sale del token, no del cuerpo.
    return AppointmentResponse.from_appointment(use_case.execute(user.user_id, payload.to_booking()))


@router.patch("/me/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_my_appointment(
    appointment_id: int,
    user: CurrentUser = Depends(current_patient_user),
    db: Session = Depends(get_db),
):
    use_case = CancelPatientAppointment(AppointmentRepository(db), PatientDirectory(PatientRepository(db)))
    return AppointmentResponse.from_appointment(use_case.execute(user.user_id, appointment_id))
