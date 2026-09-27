"""
Patrón Builder: construye una cita paso a paso con una API fluida.

Cada uso crea un builder nuevo; el orden y los valores por defecto de cada tipo de cita los
decide el `AppointmentDirector`.
"""
from datetime import date, time

from app.modules.appointment.domain.entities import Appointment, ServiceType


class AppointmentBuilder:
    def __init__(self):
        self._patient_id = 0
        self._doctor_id = 0
        self._doctor_name = ""
        self._service_type = ServiceType.CONSULTA_GENERAL
        self._date: date | None = None
        self._start_time: time | None = None
        self._end_time: time | None = None
        self._reason = "Sin especificar"
        self._notes = ""

    def patient(self, patient_id: int) -> "AppointmentBuilder":
        self._patient_id = patient_id
        return self

    def doctor(self, doctor_id: int, doctor_name: str) -> "AppointmentBuilder":
        self._doctor_id = doctor_id
        self._doctor_name = doctor_name
        return self

    def service(self, service_type: ServiceType) -> "AppointmentBuilder":
        self._service_type = service_type
        return self

    def slot(self, on_date: date, start_time: time, end_time: time) -> "AppointmentBuilder":
        self._date = on_date
        self._start_time = start_time
        self._end_time = end_time
        return self

    def reason(self, reason: str) -> "AppointmentBuilder":
        self._reason = reason
        return self

    def notes(self, notes: str) -> "AppointmentBuilder":
        self._notes = notes
        return self

    def build(self) -> Appointment:
        if self._date is None or self._start_time is None or self._end_time is None:
            raise ValueError("La cita necesita fecha, hora de inicio y hora de fin")
        return Appointment(
            patient_id=self._patient_id,
            doctor_id=self._doctor_id,
            doctor_name=self._doctor_name,
            service_type=self._service_type,
            date=self._date,
            start_time=self._start_time,
            end_time=self._end_time,
            reason=self._reason,
            notes=self._notes,
        )
