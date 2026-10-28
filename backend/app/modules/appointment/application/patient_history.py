"""
Historial de citas de un paciente, consultado por el personal a partir de su cédula (E7-HU1).
"""
from typing import Protocol

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.security import CurrentUser, Role
from app.modules.appointment.application.list_appointments import (
    AppointmentWithPatient,
    ListAppointments,
)

# ---------------------------------------------------------------- Orden y datos (2.2)

# Columnas que ve el personal. El historial es completo: incluye las citas futuras, las
# atendidas y también las canceladas, porque todas cuentan la historia del paciente.
COLUMNS = ("Fecha", "Hora", "Profesional", "Servicio", "Estado")


def newest_first(listing: list[AppointmentWithPatient]) -> list[AppointmentWithPatient]:
    """De la cita más reciente a la más antigua; el mismo día, la de hora más tarde primero."""
    return sorted(
        listing,
        key=lambda item: (item.appointment.date, item.appointment.start_time),
        reverse=True,
    )


# ---------------------------------------------------------------- Roles (2.3)

# Los que atienden o agendan al paciente, el médico (o terapista, que en el sistema también
# tiene el rol `medico`) y el agendador, más el administrador, que supervisa el centro. Un
# paciente nunca consulta el historial de otro; el suyo lo ve en "Mis citas".
HISTORY_ROLES = (Role.MEDICO, Role.AGENDADOR, Role.ADMINISTRADOR)


def ensure_can_consult(user: CurrentUser) -> None:
    if not user.has_any(HISTORY_ROLES):
        raise ForbiddenError("No tienes permiso para consultar el historial de citas de un paciente")


# ---------------------------------------------------------------- Consulta (3.2)


class PatientRegistry(Protocol):
    """Contrato que el módulo `patient` expone para saber si el paciente existe."""

    def exists(self, patient_id: int) -> bool: ...


class PatientHistoryQuery:
    def __init__(self, listing: ListAppointments, patients: PatientRegistry):
        self._listing = listing
        self._patients = patients

    def execute(self, user: CurrentUser, patient_id: int) -> list[AppointmentWithPatient]:
        """Todas las citas del paciente, de la más reciente a la más antigua."""
        ensure_can_consult(user)
        if not self._patients.exists(patient_id):
            raise NotFoundError("El paciente no existe")
        return newest_first(self._listing.by_patient(patient_id))
