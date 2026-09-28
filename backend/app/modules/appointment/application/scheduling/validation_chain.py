"""
Arma la cadena de validadores (Strategy + Chain of Responsibility) del agendamiento.

El orden importa: primero las reglas baratas sobre los datos de la propia cita y al final las
que consultan otras citas, para que el paciente reciba el motivo más directo del rechazo.
"""
from app.modules.appointment.domain.ports import (
    AuthorizationStore,
    DoctorLookup,
    PatientAppointments,
    PatientLookup,
    ScheduleLookup,
)
from app.modules.appointment.domain.validators.active_appointment_validator import (
    ActiveAppointmentValidator,
)
from app.modules.appointment.domain.validators.base import AppointmentValidator
from app.modules.appointment.domain.validators.conflict_validator import ConflictValidator
from app.modules.appointment.domain.validators.data_appointment_validator import (
    DataAppointmentValidator,
)
from app.modules.appointment.domain.validators.existence_validator import ExistenceValidator
from app.modules.appointment.domain.validators.holiday_validator import HolidayValidator
from app.modules.appointment.domain.validators.medicina_general_validator import (
    MedicinaGeneralValidator,
)
from app.modules.appointment.domain.validators.service_offered_validator import (
    ServiceOfferedValidator,
)
from app.modules.appointment.domain.validators.window_validator import AppointmentWindowValidator
from app.modules.appointment.domain.validators.working_hours_validator import (
    WorkingHoursValidator,
)
from app.shared.clock import Clock
from app.shared.holidays import ColombianHolidays


def build_validation_chain(
    *,
    appointments: PatientAppointments,
    doctors: DoctorLookup,
    patients: PatientLookup,
    schedules: ScheduleLookup,
    authorizations: AuthorizationStore,
    clock: Clock,
    holidays: ColombianHolidays,
) -> list[AppointmentValidator]:
    return [
        DataAppointmentValidator(clock),
        HolidayValidator(holidays),
        ExistenceValidator(doctors, patients),
        ServiceOfferedValidator(doctors),
        ActiveAppointmentValidator(appointments, clock),
        AppointmentWindowValidator(schedules, clock),
        WorkingHoursValidator(schedules),
        MedicinaGeneralValidator(authorizations, clock),
        ConflictValidator(),
    ]
