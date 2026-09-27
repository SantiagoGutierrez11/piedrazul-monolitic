import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_BASE_URL } from '../../../core/api-config';
import {
  AvailabilityCalendar,
  AvailableDoctor,
  DayAvailability,
  Doctor,
} from '../models/doctor.model';

// Servicio de apoyo: lista de médicos y su disponibilidad.
@Injectable({ providedIn: 'root' })
export class MedicalStaffService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${API_BASE_URL}/medical`;

  listDoctors() {
    return this.http.get<Doctor[]>(`${this.baseUrl}/doctors`);
  }

  listAvailableDoctors(specialty: string) {
    return this.http.get<AvailableDoctor[]>(`${this.baseUrl}/doctors/available`, {
      params: { specialty },
    });
  }

  getAvailability(doctorId: number, date: string) {
    return this.http.get<DayAvailability>(`${this.baseUrl}/availability`, {
      params: { doctor_id: doctorId, date },
    });
  }

  getCalendar(doctorId: number) {
    return this.http.get<AvailabilityCalendar>(`${this.baseUrl}/availability/calendar`, {
      params: { doctor_id: doctorId },
    });
  }
}
