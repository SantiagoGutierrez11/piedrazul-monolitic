from app.core.exceptions import ConflictError
from app.modules.appointment.domain.entities import Appointment
from app.modules.appointment.domain.ports import PatientAppointments
from app.modules.appointment.domain.validators.base import AppointmentValidator
from app.shared.clock import Clock


class ActiveAppointmentValidator(AppointmentValidator):
    """Un paciente solo puede tener una cita activa (agendada o reagendada) a la vez."""

    def __init__(self, appointments: PatientAppointments, clock: Clock):
        self._appointments = appointments
        self._clock = clock

    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        # La regla aplica al crear: reagendar no agrega otra cita activa.
        if appointment.appointment_id is not None:
            return
        today = self._clock.now().date()
        if self._appointments.find_active_by_patient(appointment.patient_id, today):
            raise ConflictError(
                "Ya tienes una cita agendada. Debes esperar a que sea atendida o cancelarla "
                "antes de agendar otra."
            )
