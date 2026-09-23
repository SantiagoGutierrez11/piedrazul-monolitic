import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ConfigurationService } from '../services/configuration.service';
import { DoctorScheduleItem } from '../models/configuration.model';

interface DayRow {
  dayOfWeek: number;
  label: string;
  enabled: boolean;
  startTime: string;
  endTime: string;
  intervalMinutes: number;
}

const DAY_LABELS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

function emptyWeek(): DayRow[] {
  return DAY_LABELS.map((label, index) => ({
    dayOfWeek: index + 1,
    label,
    enabled: false,
    startTime: '08:00',
    endTime: '12:00',
    intervalMinutes: 30,
  }));
}

@Component({
  selector: 'app-configuracion-profesional',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './configuracion-profesional.html',
  styleUrl: './configuracion-profesional.scss',
})
export class ConfiguracionProfesional {
  private readonly configurationService = inject(ConfigurationService);

  readonly selectedDoctorId = signal<number | null>(null);
  readonly week = signal<DayRow[]>(emptyWeek());
  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly loaded = signal(false);
  readonly message = signal('');
  readonly error = signal('');

  cargar(): void {
    const doctorId = this.selectedDoctorId();
    if (!doctorId) {
      this.error.set('Indica el ID del profesional.');
      return;
    }

    this.loading.set(true);
    this.message.set('');
    this.error.set('');

    this.configurationService.getDoctorSchedule(doctorId).subscribe({
      next: (schedules) => {
        this.week.set(this.merge(schedules));
        this.loading.set(false);
        this.loaded.set(true);
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
      return;
    }

    const schedules: DoctorScheduleItem[] = this.week()
      .filter((day) => day.enabled)
      .map((day) => ({
        dayOfWeek: day.dayOfWeek,
        startTime: day.startTime,
        endTime: day.endTime,
        intervalMinutes: day.intervalMinutes,
      }));

    this.saving.set(true);
    this.message.set('');
    this.error.set('');

    this.configurationService.updateDoctorSchedule(doctorId, schedules).subscribe({
      next: () => {
        this.message.set('Horario guardado.');
        this.saving.set(false);
      },
      error: (response) => {
        this.error.set(response?.error?.message ?? 'No se pudo guardar el horario.');
        this.saving.set(false);
      },
    });
  }

  actualizarDia(dayOfWeek: number, cambios: Partial<DayRow>): void {
    this.week.update((days) =>
      days.map((day) => (day.dayOfWeek === dayOfWeek ? { ...day, ...cambios } : day)),
    );
  }

  private merge(schedules: DoctorScheduleItem[]): DayRow[] {
    return emptyWeek().map((day) => {
      const saved = schedules.find((item) => item.dayOfWeek === day.dayOfWeek);
      if (!saved) {
        return day;
      }
      return {
        ...day,
        enabled: true,
        // El backend devuelve HH:mm:ss; <input type="time"> trabaja con HH:mm.
        startTime: saved.startTime.slice(0, 5),
        endTime: saved.endTime.slice(0, 5),
        intervalMinutes: saved.intervalMinutes,
      };
    });
  }
}
