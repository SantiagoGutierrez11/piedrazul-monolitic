import { HttpErrorResponse } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { mensajeDeError } from '../../shared/error-messages';
import { fechaLarga, horaAmPm, hoyIso } from '../../shared/fechas';
import { Appointment } from '../appointments/models/appointment.model';
import { AppointmentService } from '../appointments/services/appointment.service';
import { separarCitas } from './citas';

// Estado compartido por Inicio y Mis Citas: las citas del paciente y su cancelación.
// Se provee en cada componente, así cada pantalla carga sus datos al abrirse.
@Injectable()
export class CitasDelPaciente {
  private readonly appointmentService = inject(AppointmentService);

  readonly citas = signal<Appointment[] | null>(null);
  readonly error = signal('');
  readonly aviso = signal('');
  readonly porCancelar = signal<Appointment | null>(null);
  readonly cancelando = signal(false);

  private readonly separadas = computed(() => separarCitas(this.citas() ?? [], hoyIso()));
  readonly proximas = computed(() => this.separadas().proximas);
  readonly historial = computed(() => this.separadas().historial);

  readonly mensajeCancelacion = computed(() => {
    const cita = this.porCancelar();
    return cita
      ? `Tu cita del ${fechaLarga(cita.date)} a las ${horaAmPm(cita.startTime)} con ${cita.doctorName} quedará cancelada y el horario se liberará para otros pacientes.`
      : '';
  });

  cargar(): void {
    this.appointmentService.mine().subscribe({
      next: (citas) => this.citas.set(citas),
      error: (response: HttpErrorResponse) => {
        this.citas.set([]);
        this.error.set(mensajeDeError(response, 'No fue posible cargar tus citas.'));
      },
    });
  }

  pedirCancelacion(cita: Appointment): void {
    this.aviso.set('');
    this.error.set('');
    this.porCancelar.set(cita);
  }

  descartarCancelacion(): void {
    this.porCancelar.set(null);
  }

  confirmarCancelacion(): void {
    const cita = this.porCancelar();
    if (!cita) {
      return;
    }
    this.cancelando.set(true);
    this.appointmentService.cancelMine(cita.appointmentId).subscribe({
      next: () => {
        this.cancelando.set(false);
        this.porCancelar.set(null);
        this.aviso.set('Tu cita fue cancelada.');
        this.cargar();
      },
      error: (response: HttpErrorResponse) => {
        this.cancelando.set(false);
        this.porCancelar.set(null);
        this.error.set(mensajeDeError(response, 'No fue posible cancelar la cita.'));
      },
    });
  }
}
