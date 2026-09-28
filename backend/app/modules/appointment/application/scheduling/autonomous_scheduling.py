"""Agendamiento que hace el propio paciente desde la web (agendamiento autónomo)."""
from app.modules.appointment.application.scheduling.base import AppointmentSchedulingTemplate
from app.modules.appointment.domain.entities import Appointment


class AutonomousAppointmentScheduling(AppointmentSchedulingTemplate):
    def _assign_status(self, appointment: Appointment) -> None:
        appointment.schedule()
