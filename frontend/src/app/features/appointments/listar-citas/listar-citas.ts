import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AppointmentService } from '../services/appointment.service';
import { Appointment, AppointmentStatus, ServiceType } from '../models/appointment.model';
import { MedicalStaffService } from '../../medical-staff/services/medical-staff.service';
import { Doctor } from '../../medical-staff/models/doctor.model';

const PAGE_SIZE = 10;

/** Mensajes que ve el usuario al exportar la agenda a CSV. */
export const MENSAJES_EXPORTACION = {
  faltanFiltros: 'Selecciona un profesional y una fecha para exportar las citas.',
  sinCitas: 'No hay citas para exportar del profesional en la fecha seleccionada.',
  sinPermiso: 'Solo puedes exportar tu propia agenda.',
  error: 'No se pudo generar el archivo. Intenta de nuevo en unos minutos.',
  descargado: (archivo: string) => `Se descargó el archivo ${archivo}.`,
} as const;

/** Nombre que el backend le da al archivo en la cabecera Content-Disposition. */
function nombreDelArchivo(contentDisposition: string | null, fecha: string): string {
  return /filename="([^"]+)"/.exec(contentDisposition ?? '')?.[1] ?? `citas_${fecha}.csv`;
}

function descargar(archivo: Blob, nombre: string): void {
  const url = URL.createObjectURL(archivo);
  const enlace = document.createElement('a');
  enlace.href = url;
  enlace.download = nombre;
  enlace.click();
  URL.revokeObjectURL(url);
}

@Component({
  selector: 'app-listar-citas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './listar-citas.html',
  styleUrl: './listar-citas.scss',
})
export class ListarCitas implements OnInit {
  private readonly appointmentService = inject(AppointmentService);
  private readonly medicalStaffService = inject(MedicalStaffService);

  readonly serviceTypes: ServiceType[] = [
    'CONSULTA_GENERAL',
    'FISIOTERAPIA',
    'QUIROPRAXIA',
    'TERAPIA_NEURAL',
  ];
  readonly statuses: AppointmentStatus[] = ['AGENDADA', 'REAGENDADA', 'ATENDIDA', 'CANCELADA'];

  readonly doctors = signal<Doctor[]>([]);
  readonly selectedDoctorId = signal<number | null>(null);
  readonly selectedDate = signal<string>('');
  readonly selectedServiceType = signal<ServiceType | ''>('');
  readonly selectedStatus = signal<AppointmentStatus | ''>('');

  readonly appointments = signal<Appointment[]>([]);
  readonly loading = signal(false);
  readonly error = signal('');
  readonly searched = signal(false);

  readonly mostrarFaltantes = signal(false);
  readonly exportando = signal(false);
  readonly avisoExportacion = signal('');
  readonly exportacionExitosa = signal('');

  readonly page = signal(1);
  readonly totalPages = computed(() =>
    Math.max(1, Math.ceil(this.appointments().length / PAGE_SIZE)),
  );
  readonly pageAppointments = computed(() => {
    const start = (this.page() - 1) * PAGE_SIZE;
    return this.appointments().slice(start, start + PAGE_SIZE);
  });

  ngOnInit(): void {
    this.medicalStaffService.listDoctors().subscribe({
      next: (data) => this.doctors.set(data),
      error: () => this.error.set('No se pudo cargar la lista de profesionales.'),
    });
  }

  buscar(): void {
    const doctorId = this.selectedDoctorId();
    const date = this.selectedDate();
    this.avisoExportacion.set('');
    this.exportacionExitosa.set('');
    if (!doctorId || !date) {
      this.mostrarFaltantes.set(true);
      this.error.set('Selecciona un profesional y una fecha.');
      return;
    }

    this.mostrarFaltantes.set(false);
    this.loading.set(true);
    this.error.set('');
    this.page.set(1);

    this.appointmentService
      .listByDoctorAndDate(doctorId, date, {
        serviceType: this.selectedServiceType() || null,
        status: this.selectedStatus() || null,
      })
      .subscribe({
        next: (data) => {
          this.appointments.set(data);
          this.loading.set(false);
          this.searched.set(true);
        },
        error: () => {
          this.appointments.set([]);
          this.error.set('No se pudo consultar la agenda. Verifica que el backend esté arriba.');
          this.loading.set(false);
          this.searched.set(true);
        },
      });
  }

  /** Exporta a CSV la agenda del profesional en la fecha elegida. */
  exportarCsv(): void {
    const doctorId = this.selectedDoctorId();
    const date = this.selectedDate();
    this.avisoExportacion.set('');
    this.exportacionExitosa.set('');
    if (!doctorId || !date) {
      this.mostrarFaltantes.set(true);
      this.error.set(MENSAJES_EXPORTACION.faltanFiltros);
      return;
    }

    this.mostrarFaltantes.set(false);
    this.error.set('');
    this.exportando.set(true);

    



    this.appointmentService.exportCsv(doctorId, date).subscribe({
      next: (response) => {
        this.exportando.set(false);
        if (response.status === 204 || !response.body) {
          this.avisoExportacion.set(MENSAJES_EXPORTACION.sinCitas);
          return;
        }
        const nombre = nombreDelArchivo(response.headers.get('Content-Disposition'), date);
        descargar(response.body, nombre);
        this.exportacionExitosa.set(MENSAJES_EXPORTACION.descargado(nombre));
      },
      error: (error: HttpErrorResponse) => {
        this.exportando.set(false);
        this.error.set(
          error.status === 403 ? MENSAJES_EXPORTACION.sinPermiso : MENSAJES_EXPORTACION.error,
        );
      },
    });
  }

  cambiarPagina(delta: number): void {
    this.page.update((current) => Math.min(Math.max(1, current + delta), this.totalPages()));
  }
}
