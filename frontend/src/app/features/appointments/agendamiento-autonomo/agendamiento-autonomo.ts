import { HttpErrorResponse } from '@angular/common/http';
import { Component, HostListener, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AvailableDoctor, DayAvailability, Slot } from '../../medical-staff/models/doctor.model';
import { MedicalStaffService } from '../../medical-staff/services/medical-staff.service';
import {
  aFecha,
  aIso,
  fechaCompleta,
  fechaLarga,
  horaAmPm,
  hoyIso,
  MESES,
} from '../../../shared/fechas';
import { mensajeDeError } from '../../../shared/error-messages';
import {
  Appointment,
  SERVICE_LABELS,
  SchedulingOptions,
  ServiceOption,
  ServiceType,
} from '../models/appointment.model';
import { AppointmentService } from '../services/appointment.service';

const DESCRIPCIONES: Record<ServiceType, string> = {
  CONSULTA_GENERAL: 'Valoración médica general. Desde aquí el médico puede remitirte a otros servicios.',
  FISIOTERAPIA: 'Rehabilitación física y terapia del movimiento.',
  QUIROPRAXIA: 'Ajustes de columna y articulaciones para aliviar el dolor.',
  TERAPIA_NEURAL: 'Tratamiento del dolor y la inflamación con terapia neural.',
};

const HORARIO_OCUPADO = 'Ese horario ya no está disponible';

interface DiaCalendario {
  dia: number;
  iso: string;
  cupos: number | null; // null: el profesional no atiende o está fuera de la ventana
}

// Agendamiento autónomo del paciente en cuatro pasos: servicio -> profesional -> fecha y hora
// -> confirmación. Las reglas (festivos, ventana, horario, autorización, cita activa...) las
// aplica el backend; aquí solo se ofrecen las opciones que el backend reporta como válidas.
@Component({
  selector: 'app-agendamiento-autonomo',
  imports: [FormsModule, RouterLink],
  templateUrl: './agendamiento-autonomo.html',
  styleUrl: './agendamiento-autonomo.scss',
})
export class AgendamientoAutonomo implements OnInit {
  private readonly appointmentService = inject(AppointmentService);
  private readonly medicalStaffService = inject(MedicalStaffService);

  readonly pasos = ['Especialidad', 'Profesional', 'Fecha y Hora', 'Confirmación'];
  readonly diasSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
  readonly descripciones = DESCRIPCIONES;
  readonly etiquetas = SERVICE_LABELS;
  readonly fechaLarga = fechaLarga;
  readonly fechaCompleta = fechaCompleta;
  readonly horaAmPm = horaAmPm;

  readonly paso = signal(0);
  readonly cargando = signal(true);
  readonly error = signal('');
  readonly opciones = signal<SchedulingOptions | null>(null);

  readonly servicio = signal<ServiceOption | null>(null);
  readonly profesionales = signal<AvailableDoctor[] | null>(null);
  readonly profesional = signal<AvailableDoctor | null>(null);

  readonly cupos = signal<Map<string, number>>(new Map());
  readonly ultimaFecha = signal(hoyIso());
  readonly mesVisible = signal(primerDiaDelMes(hoyIso()));
  readonly fecha = signal<string | null>(null);
  readonly disponibilidad = signal<DayAvailability | null>(null);
  readonly hora = signal<Slot | null>(null);
  readonly listaAbierta = signal(false);

  readonly motivo = signal('');
  readonly enviando = signal(false);
  readonly citaAgendada = signal<Appointment | null>(null);

  readonly puedeAvanzar = computed(() => {
    switch (this.paso()) {
      case 0:
        return !!this.servicio()?.allowed;
      case 1:
        return !!this.profesional()?.nextAvailableDate;
      case 2:
        return !!this.fecha() && !!this.hora();
      default:
        return false;
    }
  });

  readonly tituloMes = computed(() => {
    const mes = aFecha(this.mesVisible());
    return `${capitalizar(MESES[mes.getMonth()])} ${mes.getFullYear()}`;
  });

  readonly hayMesAnterior = computed(() => this.mesVisible() > primerDiaDelMes(hoyIso()));
  readonly hayMesSiguiente = computed(
    () => this.mesVisible() < primerDiaDelMes(this.ultimaFecha()),
  );

  readonly celdas = computed<(DiaCalendario | null)[]>(() => {
    const inicio = aFecha(this.mesVisible());
    const diasDelMes = new Date(inicio.getFullYear(), inicio.getMonth() + 1, 0).getDate();
    const celdas: (DiaCalendario | null)[] = Array(inicio.getDay()).fill(null);
    for (let dia = 1; dia <= diasDelMes; dia++) {
      const iso = aIso(new Date(inicio.getFullYear(), inicio.getMonth(), dia));
      celdas.push({ dia, iso, cupos: this.cupos().get(iso) ?? null });
    }
    return celdas;
  });

  readonly horariosLibres = computed(
    () => this.disponibilidad()?.slots.filter((slot) => slot.available).length ?? 0,
  );

  readonly horaFin = computed(() => {
    const hora = this.hora();
    const intervalo = this.disponibilidad()?.intervalMinutes;
    if (!hora || !intervalo) {
      return '';
    }
    const [h, m] = hora.time.split(':').map(Number);
    const fin = h * 60 + m + intervalo;
    return `${String(Math.floor(fin / 60)).padStart(2, '0')}:${String(fin % 60).padStart(2, '0')}`;
  });

  ngOnInit(): void {
    this.cargarOpciones();
  }

  // ---------------------------------------------------------------- Paso 1: servicio

  elegirServicio(opcion: ServiceOption): void {
    if (!opcion.allowed) {
      return;
    }
    this.servicio.set(opcion);
    this.profesional.set(null);
    this.profesionales.set(null);
    this.limpiarFecha();
  }

  // ---------------------------------------------------------------- Paso 2: profesional

  elegirProfesional(doctor: AvailableDoctor): void {
    if (!doctor.nextAvailableDate) {
      return;
    }
    this.profesional.set(doctor);
    this.limpiarFecha();
  }

  iniciales(nombre: string): string {
    return nombre
      .replace(/^(Dra?\.)\s+/, '')
      .split(/\s+/)
      .slice(0, 2)
      .map((parte) => parte.charAt(0).toUpperCase())
      .join('');
  }

  // ---------------------------------------------------------------- Paso 3: fecha y hora

  cambiarMes(delta: number): void {
    const mes = aFecha(this.mesVisible());
    this.mesVisible.set(aIso(new Date(mes.getFullYear(), mes.getMonth() + delta, 1)));
  }

  elegirFecha(dia: DiaCalendario): void {
    if (!dia.cupos) {
      return;
    }
    this.fecha.set(dia.iso);
    this.hora.set(null);
    this.listaAbierta.set(false);
    this.cargarDisponibilidad();
  }

  elegirHora(slot: Slot): void {
    if (!slot.available) {
      return;
    }
    this.hora.set(slot);
    this.listaAbierta.set(false);
  }

  @HostListener('document:keydown.escape')
  cerrarLista(): void {
    this.listaAbierta.set(false);
  }

  // ---------------------------------------------------------------- Navegación

  siguiente(): void {
    if (!this.puedeAvanzar()) {
      return;
    }
    this.error.set('');
    const paso = this.paso();
    if (paso === 0 && !this.profesionales()) {
      this.cargarProfesionales();
    }
    if (paso === 1 && !this.fecha()) {
      this.cargarCalendario();
    }
    this.paso.set(paso + 1);
  }

  anterior(): void {
    this.error.set('');
    this.listaAbierta.set(false);
    this.paso.update((paso) => Math.max(paso - 1, 0));
  }

  // ---------------------------------------------------------------- Paso 4: confirmación

  confirmar(): void {
    const servicio = this.servicio();
    const profesional = this.profesional();
    const fecha = this.fecha();
    const hora = this.hora();
    if (!servicio || !profesional || !fecha || !hora || this.enviando()) {
      return;
    }

    this.enviando.set(true);
    this.error.set('');
    this.appointmentService
      .scheduleAutonomous({
        doctorId: profesional.doctorId,
        serviceType: servicio.serviceType,
        date: fecha,
        startTime: hora.time,
        reason: this.motivo().trim(),
      })
      .subscribe({
        next: (cita) => {
          this.enviando.set(false);
          this.citaAgendada.set(cita);
        },
        error: (response: HttpErrorResponse) => {
          this.enviando.set(false);
          const mensaje = mensajeDelServidor(response);
          this.error.set(mensaje);
          if (mensaje.startsWith(HORARIO_OCUPADO)) {
            // Otra persona tomó la franja: se vuelve a elegir con la disponibilidad actualizada.
            this.hora.set(null);
            this.paso.set(2);
            this.cargarCalendario();
            this.cargarDisponibilidad();
          }
        },
      });
  }

  // ---------------------------------------------------------------- Carga de datos

  private cargarOpciones(): void {
    this.cargando.set(true);
    this.appointmentService.schedulingOptions().subscribe({
      next: (opciones) => {
        this.opciones.set(opciones);
        this.ultimaFecha.set(opciones.lastBookableDate);
        this.cargando.set(false);
      },
      error: (response: HttpErrorResponse) => {
        this.error.set(mensajeDelServidor(response));
        this.cargando.set(false);
      },
    });
  }

  private cargarProfesionales(): void {
    const servicio = this.servicio();
    if (!servicio) {
      return;
    }
    this.medicalStaffService.listAvailableDoctors(servicio.specialty).subscribe({
      next: (profesionales) => this.profesionales.set(profesionales),
      error: (response: HttpErrorResponse) => {
        this.profesionales.set([]);
        this.error.set(mensajeDelServidor(response));
      },
    });
  }

  private cargarCalendario(): void {
    const profesional = this.profesional();
    if (!profesional) {
      return;
    }
    this.medicalStaffService.getCalendar(profesional.doctorId).subscribe({
      next: (calendario) => {
        this.cupos.set(new Map(calendario.days.map((dia) => [dia.date, dia.availableSlots])));
        this.ultimaFecha.set(calendario.lastBookableDate);
        if (!this.fecha() && profesional.nextAvailableDate) {
          this.mesVisible.set(primerDiaDelMes(profesional.nextAvailableDate));
        }
      },
      error: (response: HttpErrorResponse) => this.error.set(mensajeDelServidor(response)),
    });
  }

  private cargarDisponibilidad(): void {
    const profesional = this.profesional();
    const fecha = this.fecha();
    if (!profesional || !fecha) {
      return;
    }
    this.disponibilidad.set(null);
    this.medicalStaffService.getAvailability(profesional.doctorId, fecha).subscribe({
      next: (disponibilidad) => this.disponibilidad.set(disponibilidad),
      error: (response: HttpErrorResponse) => this.error.set(mensajeDelServidor(response)),
    });
  }

  private limpiarFecha(): void {
    this.fecha.set(null);
    this.hora.set(null);
    this.disponibilidad.set(null);
    this.cupos.set(new Map());
  }
}

function primerDiaDelMes(iso: string): string {
  return `${iso.slice(0, 7)}-01`;
}

function capitalizar(texto: string): string {
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function mensajeDelServidor(response: HttpErrorResponse): string {
  return mensajeDeError(response, 'Ocurrió un error. Intenta de nuevo.');
}
