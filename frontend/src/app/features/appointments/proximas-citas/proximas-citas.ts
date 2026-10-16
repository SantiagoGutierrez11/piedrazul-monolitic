import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../core/auth/auth.service';
import { mensajeDeError } from '../../../shared/error-messages';
import { MESES, aFecha, fechaLarga, horaAmPm } from '../../../shared/fechas';
import { Doctor } from '../../medical-staff/models/doctor.model';
import { MedicalStaffService } from '../../medical-staff/services/medical-staff.service';
import {
  Appointment,
  SERVICE_LABELS,
  STATUS_LABELS,
  UpcomingAppointments,
  UpcomingWeek,
} from '../models/appointment.model';
import { AppointmentService } from '../services/appointment.service';

export const OPCIONES_SEMANAS = [2, 4, 8];

interface DiaConCitas {
  fecha: string;
  titulo: string;
  citas: Appointment[];
}

interface SemanaVista {
  inicio: string;
  etiqueta: string;
  rango: string;
  total: number;
  ancho: number; // % de la barra respecto a la semana con más citas
  dias: DiaConCitas[];
}

/** "Esta semana", "Próxima semana", "En 2 semanas"... */
export function etiquetaSemana(indice: number): string {
  if (indice === 0) {
    return 'Esta semana';
  }
  return indice === 1 ? 'Próxima semana' : `En ${indice} semanas`;
}

/** "12 al 18 de octubre" o "26 de octubre al 1 de noviembre". */
export function rangoSemana(inicio: string, fin: string): string {
  const desde = aFecha(inicio);
  const hasta = aFecha(fin);
  const mesFin = MESES[hasta.getMonth()];
  return desde.getMonth() === hasta.getMonth()
    ? `${desde.getDate()} al ${hasta.getDate()} de ${mesFin}`
    : `${desde.getDate()} de ${MESES[desde.getMonth()]} al ${hasta.getDate()} de ${mesFin}`;
}

function porDia(citas: Appointment[]): DiaConCitas[] {
  const dias = new Map<string, Appointment[]>();
  for (const cita of citas) {
    dias.set(cita.date, [...(dias.get(cita.date) ?? []), cita]);
  }
  return [...dias].map(([fecha, citasDelDia]) => ({
    fecha,
    titulo: fechaLarga(fecha),
    citas: citasDelDia,
  }));
}

// Reporte de próximas citas por semana para el médico (solo las suyas), el agendador y el administrador.
@Component({
  selector: 'app-proximas-citas',
  imports: [FormsModule],
  templateUrl: './proximas-citas.html',
  styleUrl: './proximas-citas.scss',
})
export class ProximasCitas implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly citasApi = inject(AppointmentService);
  private readonly medicosApi = inject(MedicalStaffService);

  readonly horaAmPm = horaAmPm;
  readonly servicios = SERVICE_LABELS;
  readonly estados = STATUS_LABELS;
  readonly opcionesSemanas = OPCIONES_SEMANAS;
  // El médico solo ve su propia agenda, así que no elige profesional.
  readonly verTodoElCentro = this.auth.hasRole('agendador', 'administrador');

  readonly medicos = signal<Doctor[]>([]);
  readonly medicoId = signal<number | null>(null);
  readonly semanas = signal(4);
  readonly reporte = signal<UpcomingAppointments | null>(null);
  readonly error = signal('');

  readonly periodo = computed(() => {
    const reporte = this.reporte();
    return reporte ? `Del ${fechaLarga(reporte.dateFrom)} al ${fechaLarga(reporte.dateTo)}` : '';
  });

  readonly vista = computed<SemanaVista[]>(() => {
    const semanas = this.reporte()?.weeks ?? [];
    const maximo = Math.max(1, ...semanas.map((semana) => semana.total));
    return semanas.map((semana: UpcomingWeek, indice) => ({
      inicio: semana.start,
      etiqueta: etiquetaSemana(indice),
      rango: rangoSemana(semana.start, semana.end),
      total: semana.total,
      ancho: Math.round((semana.total / maximo) * 100),
      dias: porDia(semana.appointments),
    }));
  });

  readonly estaSemana = computed(() => this.reporte()?.weeks[0]?.total ?? 0);

  readonly semanaPico = computed(() => {
    const conCitas = this.vista().filter((semana) => semana.total > 0);
    if (conCitas.length === 0) {
      return null;
    }
    return conCitas.reduce((pico, semana) => (semana.total > pico.total ? semana : pico));
  });

  ngOnInit(): void {
    if (this.verTodoElCentro) {
      this.medicosApi.listDoctors().subscribe({ next: (medicos) => this.medicos.set(medicos) });
    }
    this.cargar();
  }

  cambiarMedico(valor: string): void {
    this.medicoId.set(valor ? Number(valor) : null);
    this.cargar();
  }

  cambiarSemanas(valor: string): void {
    this.semanas.set(Number(valor));
    this.cargar();
  }

  cargar(): void {
    this.reporte.set(null);
    this.error.set('');
    this.citasApi.upcoming(this.semanas(), this.medicoId()).subscribe({
      next: (reporte) => this.reporte.set(reporte),
      error: (err) => {
        this.reporte.set({ dateFrom: '', dateTo: '', total: 0, weeks: [] });
        this.error.set(mensajeDeError(err, 'No se pudieron cargar las próximas citas.'));
      },
    });
  }

  irASemana(inicio: string): void {
    document.getElementById(`semana-${inicio}`)?.scrollIntoView({ behavior: 'smooth' });
  }
}
