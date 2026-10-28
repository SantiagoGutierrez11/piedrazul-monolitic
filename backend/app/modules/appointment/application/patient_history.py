"""
Historial de citas de un paciente, consultado por el personal a partir de su cédula (E7-HU1).
"""
from app.core.exceptions import ForbiddenError
from app.core.security import CurrentUser, Role
from app.modules.appointment.application.list_appointments import AppointmentWithPatient

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
