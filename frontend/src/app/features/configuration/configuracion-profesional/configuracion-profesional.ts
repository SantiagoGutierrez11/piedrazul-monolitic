import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ConfigurationService } from '../services/configuration.service';
import { DoctorScheduleItem } from '../models/configuration.model';
import { MedicalStaffService } from '../../medical-staff/services/medical-staff.service';
import { Doctor } from '../../medical-staff/models/doctor.model';

interface DayOption {
  dayOfWeek: number;
  label: string;
  selected: boolean;
}

const DAY_LABELS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

function allDays(): DayOption[] {
  return DAY_LABELS.map((label, index) => ({
    dayOfWeek: index + 1,
    label,
    selected: false,
  }));
}

@Component({
  selector: 'app-configuracion-profesional',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './configuracion-profesional.html',
  styleUrl: './configuracion-profesional.scss',
})
export class ConfiguracionProfesional implements OnInit {
  private readonly configurationService = inject(ConfigurationService);
  private readonly medicalStaffService = inject(MedicalStaffService);
  private readonly router = inject(Router);

  readonly doctors = signal<Doctor[]>([]);
  readonly selectedDoctorId = signal<number | null>(null);
  readonly days = signal<DayOption[]>(allDays());
  readonly startTime = signal('08:00');
  readonly endTime = signal('18:00');
  readonly intervalMinutes = signal(30);

  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly message = signal('');
  readonly error = signal('');

  ngOnInit(): void {
    this.medicalStaffService.listDoctors().subscribe({
      next: (data) => this.doctors.set(data),
      error: () => this.error.set('No se pudo cargar la lista de profesionales.'),
    });
  }

  seleccionarDoctor(doctorId: number | null): void {
    this.selectedDoctorId.set(doctorId);
    this.days.set(allDays());
    if (doctorId) {
      this.cargar();
    }
  }

  cargar(): void {
    const doctorId = this.selectedDoctorId();
    if (!doctorId) {
      this.error.set('Selecciona un profesional.');
      return;
    }

    this.loading.set(true);
    this.message.set('');
    this.error.set('');

    this.configurationService.getDoctorSchedule(doctorId).subscribe({
      next: (schedules) => {
        this.aplicar(schedules);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se pudo cargar el horario del profesional.');
        this.loading.set(false);
      },
    });
  }

  guardar(): void {
    const doctorId = this.selectedDoctorId();
    if (!doctorId) {
      this.error.set('Selecciona un profesional.');
      return;
    }

    const schedules: DoctorScheduleItem[] = this.days()
      .filter((day) => day.selected)
      .map((day) => ({
        dayOfWeek: day.dayOfWeek,
        startTime: this.startTime(),
        endTime: this.endTime(),
        intervalMinutes: this.intervalMinutes(),
      }));

    this.saving.set(true);
    this.message.set('');
    this.error.set('');

    this.configurationService.updateDoctorSchedule(doctorId, schedules).subscribe({
      next: () => {
        this.message.set('Disponibilidad guardada.');
        this.saving.set(false);
      },
      error: (response) => {
        this.error.set(response?.error?.message ?? 'No se pudo guardar la disponibilidad.');
        this.saving.set(false);
      },
    });
  }

  alternarDia(dayOfWeek: number, selected: boolean): void {
    this.days.update((days) =>
      days.map((day) => (day.dayOfWeek === dayOfWeek ? { ...day, selected } : day)),
    );
  }

  cancelar(): void {
    this.router.navigate(['/configuration']);
  }

  private aplicar(schedules: DoctorScheduleItem[]): void {
    this.days.update((days) =>
      days.map((day) => ({
        ...day,
        selected: schedules.some((item) => item.dayOfWeek === day.dayOfWeek),
      })),
    );

    const primero = schedules[0];
    if (primero) {
      // El backend guarda la franja por día; el formulario usa una sola franja para
      // todos los días marcados, así que toma la del primer día configurado.
      this.startTime.set(primero.startTime.slice(0, 5));
      this.endTime.set(primero.endTime.slice(0, 5));
      this.intervalMinutes.set(primero.intervalMinutes);
    }
  }
}
