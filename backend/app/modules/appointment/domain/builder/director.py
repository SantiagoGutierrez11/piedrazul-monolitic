"""Director del patrón Builder: una receta por cada forma de crear una cita."""
from datetime import date, time

from app.modules.appointment.domain.builder.appointment_builder import AppointmentBuilder
from app.modules.appointment.domain.entities import Appointment, ServiceType

PATIENT_DEFAULT_REASON = "Cita agendada por el paciente"


class AppointmentDirector:
    def build_patient_appointment(
        self,
        *,
        patient_id: int,
        doctor_id: int,
        doctor_name: str,
        service_type: ServiceType,
        on_date: date,
        start_time: time,
        end_time: time,
        reason: str = "",
    ) -> Appointment:
        """Cita que el propio paciente agenda desde la web (agendamiento autónomo)."""
        return (
            AppointmentBuilder()
            .patient(patient_id)
            .doctor(doctor_id, doctor_name)
            .service(service_type)
            .slot(on_date, start_time, end_time)
            .reason(reason.strip() or PATIENT_DEFAULT_REASON)
            .notes("Agendamiento autónomo")
            .build()
        )

    def build_manual_appointment(
        self,
        *,
        patient_id: int,
        doctor_id: int,
        doctor_name: str,
        service_type: ServiceType,
        on_date: date,
        start_time: time,
        end_time: time,
        reason: str = "",
        notes: str = "",
    ) -> Appointment:
        """Cita que registra el agendador en nombre del paciente, con motivo y notas propias."""
        return (
            AppointmentBuilder()
            .patient(patient_id)
            .doctor(doctor_id, doctor_name)
            .service(service_type)
            .slot(on_date, start_time, end_time)
            .reason(reason.strip() or "Sin especificar")
            .notes(notes.strip())
            .build()
        )
