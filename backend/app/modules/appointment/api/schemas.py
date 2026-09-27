"""DTOs de entrada/salida de /api/v1/appointments."""
from datetime import date, datetime, time

from pydantic import Field

from app.modules.appointment.application.list_appointments import AppointmentWithPatient
from app.modules.appointment.application.scheduling.patient_scheduling import PatientBooking
from app.modules.appointment.application.scheduling_options import SchedulingOptions
from app.modules.appointment.domain.entities import Appointment, AppointmentStatus, ServiceType
from app.shared.schemas import CamelModel


class AppointmentResponse(CamelModel):
    appointment_id: int
    patient_id: int
    patient_name: str | None = None
    patient_phone: str | None = None
    doctor_id: int
    doctor_name: str
    service_type: ServiceType
    date: date
    start_time: time
    end_time: time
    reason: str
    notes: str = ""
    status: AppointmentStatus

    @classmethod
    def from_appointment(cls, appointment: Appointment) -> "AppointmentResponse":
        return cls(
            appointment_id=appointment.appointment_id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            doctor_name=appointment.doctor_name,
            service_type=appointment.service_type,
            date=appointment.date,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            reason=appointment.reason,
            notes=appointment.notes,
            status=appointment.status,
        )

    @classmethod
    def from_listing(cls, item: AppointmentWithPatient) -> "AppointmentResponse":
        response = cls.from_appointment(item.appointment)
        if item.patient:
            response.patient_name = item.patient.full_name
            response.patient_phone = item.patient.phone
        return response


class PatientBookingRequest(CamelModel):
    doctor_id: int = Field(gt=0)
    service_type: ServiceType
    date: date
    start_time: time
    reason: str = Field(default="", max_length=255)

    def to_booking(self) -> PatientBooking:
        return PatientBooking(
            doctor_id=self.doctor_id,
            service_type=self.service_type,
            date=self.date,
            start_time=self.start_time,
            reason=self.reason,
        )


class AttendRequest(CamelModel):
    # Servicio especializado que el médico autoriza al paciente (opcional).
    authorized_service_type: ServiceType | None = None


class ServiceOptionResponse(CamelModel):
    service_type: ServiceType
    label: str
    specialty: str
    allowed: bool
    locked_reason: str | None


class AuthorizationResponse(CamelModel):
    service_type: ServiceType
    label: str
    expires_at: datetime


class SchedulingOptionsResponse(CamelModel):
    services: list[ServiceOptionResponse]
    authorization: AuthorizationResponse | None
    active_appointment: AppointmentResponse | None
    window_weeks: int
    last_bookable_date: date

    @classmethod
    def from_options(cls, options: SchedulingOptions) -> "SchedulingOptionsResponse":
        authorization = options.authorization
        return cls(
            services=[
                ServiceOptionResponse(
                    service_type=option.service_type,
                    label=option.service_type.label,
                    specialty=option.service_type.specialty,
                    allowed=option.allowed,
                    locked_reason=option.locked_reason,
                )
                for option in options.services
            ],
            authorization=AuthorizationResponse(
                service_type=authorization.service_type,
                label=authorization.service_type.label,
                expires_at=authorization.expires_at,
            )
            if authorization
            else None,
            active_appointment=AppointmentResponse.from_appointment(options.active_appointment)
            if options.active_appointment
            else None,
            window_weeks=options.window_weeks,
            last_bookable_date=options.last_bookable_date,
        )
