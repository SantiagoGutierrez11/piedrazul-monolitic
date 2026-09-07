"""Usado por el agendador (o por el médico) para registrar una cita a mano."""
from app.modules.appointment.application.scheduling.base import AppointmentSchedulingTemplate
from app.modules.appointment.domain.entities import Appointment


class ManualAppointmentScheduling(AppointmentSchedulingTemplate):
    def _assign_status(self, appointment: Appointment) -> None:
        appointment.schedule()
