import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ConfirmDialog } from '../../../shared/confirm-dialog/confirm-dialog';
import { mensajeDeError } from '../../../shared/error-messages';
import { fechaCompleta, horaAmPm, hoyIso } from '../../../shared/fechas';
import {
  Appointment,
  SERVICE_LABELS,
  STATUS_LABELS,
} from '../../appointments/models/appointment.model';
import { AppointmentService } from '../../appointments/services/appointment.service';
import { Doctor } from '../../medical-staff/models/doctor.model';
import { MedicalStaffService } from '../../medical-staff/services/medical-staff.service';

const ACTIVAS = ['AGENDADA', 'REAGENDADA'];

// Panel del agendador: agenda del día de todos los profesionales, con filtros y cancelación.
@Component({
  selector: 'app-panel-agenda',
  imports: [FormsModule, ConfirmDialog],
  templateUrl: './panel-agenda.html',
  styleUrl: './panel-agenda.scss',
})
export class PanelAgenda implements OnInit {
  private readonly citasApi = inject(AppointmentService);
  private readonly medicosApi = inject(MedicalStaffService);

  readonly horaAmPm = horaAmPm;
  readonly servicios = SERVICE_LABELS;
  readonly estados = STATUS_LABELS;
  readonly hoy = hoyIso();

  readonly medicos = signal<Doctor[]>([]);
  readonly medicoId = signal<number | null>(null);
  readonly fecha = signal(hoyIso());
  readonly citas = signal<Appointment[] | null>(null);
  readonly error = signal('');
  readonly aviso = signal('');
  readonly porCancelar = signal<Appointment | null>(null);
  readonly cancelando = signal(false);

  readonly titulo = computed(() => (this.fecha() === this.hoy ? 'Agenda del día' : 'Agenda'));
  readonly fechaTexto = computed(() => fechaCompleta(this.fecha()));
  readonly activas = computed(() => (this.citas() ?? []).filter((c) => ACTIVAS.includes(c.status)));
  readonly canceladas = computed(
    () => (this.citas() ?? []).filter((c) => c.status === 'CANCELADA').length,
  );
  readonly total = computed(() => (this.citas() ?? []).length - this.canceladas());

  // Solo tiene sentido hablar de "próxima" cita en la agenda de hoy.
  readonly proxima = computed(() => {
    if (this.fecha() !== this.hoy) {
      return null;
    }
    const ahora = new Date().toTimeString().slice(0, 8);
    return this.activas().find((c) => c.startTime >= ahora) ?? null;
  });

  readonly mensajeCancelacion = computed(() => {
    const cita = this.porCancelar();
    return cita
      ? `Se cancelará la cita de ${cita.patientName ?? 'el paciente'} con ${cita.doctorName} ` +
          `a las ${horaAmPm(cita.startTime)}. Esta acción no se puede deshacer.`
      : '';
  });

  ngOnInit(): void {
    this.medicosApi.listDoctors().subscribe({ next: (medicos) => this.medicos.set(medicos) });
    this.cargar();
  }

  cambiarMedico(valor: string): void {
    this.medicoId.set(valor ? Number(valor) : null);
    this.cargar();
  }

  cambiarFecha(valor: string): void {
    if (valor) {
      this.fecha.set(valor);
      this.cargar();
    }
  }

  cargar(): void {
    this.citas.set(null);
    this.error.set('');
    this.citasApi.listByDate(this.fecha(), this.medicoId()).subscribe({
      next: (citas) => this.citas.set(citas),
      error: (err) => {
        this.citas.set([]);
        this.error.set(mensajeDeError(err, 'No se pudo cargar la agenda.'));
      },
    });
  }

  esActiva(cita: Appointment): boolean {
    return ACTIVAS.includes(cita.status);
  }

  confirmarCancelacion(): void {
    const cita = this.porCancelar();
    if (!cita) {
      return;
    }
    this.cancelando.set(true);
    this.citasApi.cancel(cita.appointmentId).subscribe({
      next: (cancelada) => {
        this.citas.update((citas) =>
          (citas ?? []).map((c) => (c.appointmentId === cancelada.appointmentId ? cancelada : c)),
        );
        this.aviso.set('La cita fue cancelada.');
        this.cancelando.set(false);
        this.porCancelar.set(null);
      },
      error: (err) => {
        this.error.set(mensajeDeError(err, 'No se pudo cancelar la cita.'));
        this.cancelando.set(false);
        this.porCancelar.set(null);
      },
    });
  }
}
