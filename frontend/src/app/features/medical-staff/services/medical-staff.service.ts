import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_BASE_URL } from '../../../core/api-config';
import { Doctor } from '../models/doctor.model';

// Servicio de apoyo: lista de médicos y su disponibilidad.
@Injectable({ providedIn: 'root' })
export class MedicalStaffService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${API_BASE_URL}/medical`;

  listDoctors() {
    return this.http.get<Doctor[]>(`${this.baseUrl}/doctors`);
  }

  getAvailability(doctorId: number, date: string) {
    return this.http.get<string[]>(`${this.baseUrl}/availability`, {
      params: { doctorId, date },
    });
  }
}
