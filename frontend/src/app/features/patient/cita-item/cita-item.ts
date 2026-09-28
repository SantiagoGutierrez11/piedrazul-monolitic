import { Component, input, output } from '@angular/core';
import { fechaLarga, horaAmPm } from '../../../shared/fechas';
import {
  Appointment,
  SERVICE_LABELS,
  STATUS_LABELS,
} from '../../appointments/models/appointment.model';

// Fila de una cita en las listas del paciente (historial y mis citas).
@Component({
  selector: 'app-cita-item',
  templateUrl: './cita-item.html',
  styleUrl: './cita-item.scss',
})
export class CitaItem {
  readonly cita = input.required<Appointment>();
  readonly cancelable = input(false);
  readonly cancelar = output<Appointment>();

  readonly fechaLarga = fechaLarga;
  readonly horaAmPm = horaAmPm;
  readonly servicios = SERVICE_LABELS;
  readonly estados = STATUS_LABELS;
}
