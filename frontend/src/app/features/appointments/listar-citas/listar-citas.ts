import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AppointmentService } from '../services/appointment.service';
import { Appointment, AppointmentStatus, ServiceType } from '../models/appointment.model';

const PAGE_SIZE = 10;

@Component({
  selector: 'app-listar-citas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './listar-citas.html',
  styleUrl: './listar-citas.scss',
})
export class ListarCitas {
  private readonly appointmentService = inject(AppointmentService);

  readonly serviceTypes: ServiceType[] = [
    'CONSULTA_GENERAL',
    'FISIOTERAPIA',
    'QUIROPRAXIA',
    'TERAPIA_NEURAL',
  ];
  readonly statuses: AppointmentStatus[] = ['AGENDADA', 'REAGENDADA', 'ATENDIDA', 'CANCELADA'];

  readonly selectedDoctorId = signal<number | null>(null);
  readonly selectedDate = signal<string>('');
  readonly selectedServiceType = signal<ServiceType | ''>('');
  readonly selectedStatus = signal<AppointmentStatus | ''>('');

  readonly appointments = signal<Appointment[]>([]);
  readonly loading = signal(false);
  readonly error = signal('');
  readonly searched = signal(false);

  readonly page = signal(1);
  readonly totalPages = computed(() =>
    Math.max(1, Math.ceil(this.appointments().length / PAGE_SIZE)),
  );
  readonly pageAppointments = computed(() => {
    const start = (this.page() - 1) * PAGE_SIZE;
    return this.appointments().slice(start, start + PAGE_SIZE);
  });

  buscar(): void {
    const doctorId = this.selectedDoctorId();
    const date = this.selectedDate();
    if (!doctorId || !date) {
      this.error.set('Selecciona una fecha y el ID del médico.');
      return;
    }

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

  cambiarPagina(delta: number): void {
    this.page.update((current) => Math.min(Math.max(1, current + delta), this.totalPages()));
  }
}
