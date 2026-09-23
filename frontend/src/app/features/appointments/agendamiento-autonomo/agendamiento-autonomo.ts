import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { AppointmentService } from '../services/appointment.service';

// Wizard de 4 pasos: tipo de servicio -> profesional -> fecha/hora -> confirmación.
// TODO: faltan los 4 pasos completos; por ahora solo está el esqueleto y la inyección
// de AppointmentService lista para el paso de confirmación (create()).
@Component({
  selector: 'app-agendamiento-autonomo',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './agendamiento-autonomo.html',
  styleUrl: './agendamiento-autonomo.scss',
})
export class AgendamientoAutonomo {
  private readonly appointmentService = inject(AppointmentService);

  readonly step = signal(0);
  readonly steps = ['Tipo de servicio', 'Profesional', 'Fecha y Hora', 'Confirmación'];

  next(): void {
    this.step.update((s) => Math.min(s + 1, this.steps.length - 1));
  }

  back(): void {
    this.step.update((s) => Math.max(s - 1, 0));
  }
}
