import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { forkJoin, switchMap } from 'rxjs';
import { AuthService } from '../../../core/auth/auth.service';
import { mensajeDeError } from '../../../shared/error-messages';
import { fechaCompleta, horaAmPm, hoyIso } from '../../../shared/fechas';
import { Appointment, SERVICE_LABELS } from '../../appointments/models/appointment.model';
import { AppointmentService } from '../../appointments/services/appointment.service';
import { Doctor, Slot } from '../../medical-staff/models/doctor.model';
import { MedicalStaffService } from '../../medical-staff/services/medical-staff.service';

interface Franja {
  hora: string; // HH:mm
  cita: Appointment | null;
}

const ACTIVAS = ['AGENDADA', 'REAGENDADA'];

// Panel del médico: resumen del día, próxima cita y agenda por franjas.
@Component({
  selector: 'app-panel-medico',
  templateUrl: './panel-medico.html',
  styleUrl: './panel-medico.scss',
})
export class PanelMedico implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly citasApi = inject(AppointmentService);
  private readonly medicosApi = inject(MedicalStaffService);

  readonly horaAmPm = horaAmPm;
  readonly servicios = SERVICE_LABELS;
  readonly hoy = fechaCompleta(hoyIso());

  readonly medico = signal<Doctor | null>(null);
  readonly citas = signal<Appointment[] | null>(null);
  private readonly franjasDelDia = signal<Slot[]>([]);
  readonly error = signal('');
  readonly atendiendo = signal<number | null>(null);

  readonly saludo = computed(() => {
    const hora = new Date().getHours();
    return hora < 12 ? 'Buenos días' : hora < 19 ? 'Buenas tardes' : 'Buenas noches';
  });
  readonly nombre = computed(() => this.medico()?.fullName ?? this.auth.user()?.fullName ?? '');

  private readonly delDia = computed(() =>
    (this.citas() ?? []).filter((c) => c.status !== 'CANCELADA'),
  );
  readonly atendidas = computed(() => this.delDia().filter((c) => c.status === 'ATENDIDA').length);
  readonly pendientes = computed(() => this.delDia().filter((c) => ACTIVAS.includes(c.status)));
  readonly total = computed(() => this.delDia().length);
  readonly proxima = computed(() => this.pendientes()[0] ?? null);

  // Franjas del horario del médico hoy, cada una con la cita que la ocupa (si hay).
  readonly agenda = computed<Franja[]>(() => {
    const porHora = new Map(this.delDia().map((c) => [c.startTime.slice(0, 5), c]));
    const horas = new Set([...this.franjasDelDia().map((f) => f.time), ...porHora.keys()]);
    return [...horas].sort().map((hora) => ({ hora, cita: porHora.get(hora) ?? null }));
  });

  ngOnInit(): void {
    this.medicosApi
      .myProfile()
      .pipe(
        switchMap((medico) => {
          this.medico.set(medico);
          return forkJoin({
            citas: this.citasApi.listByDoctorAndDate(medico.doctorId, hoyIso()),
            dia: this.medicosApi.getAvailability(medico.doctorId, hoyIso()),
          });
        }),
      )
      .subscribe({
        next: ({ citas, dia }) => {
          this.citas.set(citas);
          this.franjasDelDia.set(dia.slots);
        },
        error: (err) => {
          this.citas.set([]);
          this.error.set(mensajeDeError(err, 'No se pudo cargar tu agenda de hoy.'));
        },
      });
  }

  marcarAtendida(cita: Appointment): void {
    this.atendiendo.set(cita.appointmentId);
    this.citasApi.attend(cita.appointmentId).subscribe({
      next: (actualizada) => {
        this.citas.update((citas) =>
          (citas ?? []).map((c) =>
            c.appointmentId === actualizada.appointmentId ? actualizada : c,
          ),
        );
        this.atendiendo.set(null);
      },
      error: (err) => {
        this.atendiendo.set(null);
        this.error.set(mensajeDeError(err, 'No se pudo marcar la cita como atendida.'));
      },
    });
  }
}
