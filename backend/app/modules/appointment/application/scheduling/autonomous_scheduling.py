"""
Variante de agendamiento para el autoagendamiento del paciente.

Punto de extensión separado de `ManualAppointmentScheduling` para poder agregar las
reglas anti-fraude que necesita el autoagendamiento (validación de identidad, límite de
creación masiva, verificación básica de datos) sin afectar el flujo manual.

TODO: implementar esas reglas anti-fraude (propias o en un validador aparte); por ahora
el comportamiento es igual al manual.
"""
from app.modules.appointment.application.scheduling.base import AppointmentSchedulingTemplate
from app.modules.appointment.domain.entities import Appointment


class AutonomousAppointmentScheduling(AppointmentSchedulingTemplate):
    def _assign_status(self, appointment: Appointment) -> None:
        appointment.schedule()
