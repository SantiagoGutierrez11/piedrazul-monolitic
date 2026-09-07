"""
TODO: faltan más validadores (ventana de citas, feriados, medicina general, cita activa,
existencia) siguiendo este mismo patrón (un archivo por validador).
"""
from app.core.exceptions import ConflictError
from app.modules.appointment.domain.entities import Appointment, AppointmentStatus
from app.modules.appointment.domain.validators.base import AppointmentValidator


class ConflictValidator(AppointmentValidator):
    """Impide dos citas activas con el mismo médico en el mismo horario."""

    def validate(self, appointment: Appointment, existing_on_date: list[Appointment]) -> None:
        for existing in existing_on_date:
            if existing.status == AppointmentStatus.CANCELADA:
                continue
            if existing.start_time == appointment.start_time:
                raise ConflictError(
                    "Ya existe una cita activa con este médico en ese horario"
                )
