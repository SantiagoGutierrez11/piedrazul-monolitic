import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_BASE_URL } from '../../../core/api-config';
import { Appointment } from '../models/appointment.model';

// GET /patients/search: paciente sugerido al escribir la cédula.
export interface PacienteEncontrado {
  patientId: number;
  fullName: string;
  documentType: string | null;
  documentNumber: string;
  phone: string;
}

// Llamadas al backend de la pantalla Historial de Paciente (E7-HU1).
@Injectable({ providedIn: 'root' })
export class HistorialPacienteService {
  private readonly http = inject(HttpClient);

  /** Pacientes cuya cédula empieza por `documento` (máximo 8), con la coincidencia exacta primero. */
  buscar(documento: string) {
    const params = new HttpParams().set('document', documento);
    return this.http.get<PacienteEncontrado[]>(`${API_BASE_URL}/patients/search`, { params });
  }

  /** Todas las citas del paciente, de la más reciente a la más antigua. */
  historial(patientId: number) {
    return this.http.get<Appointment[]>(`${API_BASE_URL}/appointments/patient/${patientId}/history`);
  }
}
