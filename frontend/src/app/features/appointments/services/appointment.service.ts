import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_BASE_URL } from '../../../core/api-config';
import {
  Appointment,
  AppointmentStatus,
  CreateAppointmentRequest,
  ServiceType,
} from '../models/appointment.model';

// Compartido por el listado de citas y el agendamiento — coordinar cambios aquí.
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

  create(payload: CreateAppointmentRequest) {
    return this.http.post<Appointment>(this.baseUrl, payload);
  }

  listByPatient(patientId: number) {
    return this.http.get<Appointment[]>(`${this.baseUrl}/patient/${patientId}`);
  }

  cancel(appointmentId: number) {
    return this.http.patch<Appointment>(`${this.baseUrl}/${appointmentId}/cancel`, {});
  }
}
