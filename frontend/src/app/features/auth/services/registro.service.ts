import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_BASE_URL } from '../../../core/api-config';
import { PacienteRegistrado, RegistroPaciente } from '../models/registro.model';

@Injectable({ providedIn: 'root' })
export class RegistroService {
  private readonly http = inject(HttpClient);

  registrar(datos: RegistroPaciente) {
    return this.http.post<PacienteRegistrado>(`${API_BASE_URL}/patients/register`, datos);
  }
}
