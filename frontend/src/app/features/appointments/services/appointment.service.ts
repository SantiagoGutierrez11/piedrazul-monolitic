import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_BASE_URL } from '../../../core/api-config';
import {
  Appointment,
  AppointmentStatus,
  PatientBookingRequest,
  SchedulingOptions,
  ServiceType,
} from '../models/appointment.model';

// Compartido por el listado de citas, el agendamiento y las pantallas del paciente.
@Injectable({ providedIn: 'root' })
export class AppointmentService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${API_BASE_URL}/appointments`;

  listByDoctorAndDate(
    doctorId: number,
    date: string,
    filters: { serviceType?: ServiceType | null; status?: AppointmentStatus | null } = {},
  ) {
    let params = new HttpParams();
    if (filters.serviceType) {
      params = params.set('service_type', filters.serviceType);
    }
    if (filters.status) {
      params = params.set('status', filters.status);
    }

    return this.http.get<Appointment[]>(`${this.baseUrl}/doctor/${doctorId}/date/${date}`, {
      params,
    });
  }

  listByPatient(patientId: number) {
    return this.http.get<Appointment[]>(`${this.baseUrl}/patient/${patientId}`);
  }

  // ---- Paciente autenticado

  mine() {
    return this.http.get<Appointment[]>(`${this.baseUrl}/me`);
  }

  schedulingOptions() {
    return this.http.get<SchedulingOptions>(`${this.baseUrl}/me/options`);
  }

  scheduleAutonomous(request: PatientBookingRequest) {
    return this.http.post<Appointment>(`${this.baseUrl}/autonomous`, request);
  }

  cancelMine(appointmentId: number) {
    return this.http.patch<Appointment>(`${this.baseUrl}/me/${appointmentId}/cancel`, {});
  }
}
