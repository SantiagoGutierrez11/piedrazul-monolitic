import { HttpClient } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin, map, of, switchMap } from 'rxjs';
import { API_BASE_URL } from '../../../core/api-config';
import { mensajeDeError } from '../../../shared/error-messages';
import { DIAS, aFecha, fechaCompleta, horaAmPm, hoyIso } from '../../../shared/fechas';
import { AppointmentSummary } from '../../appointments/models/appointment.model';
import { AppointmentService } from '../../appointments/services/appointment.service';
import { DoctorScheduleItem } from '../../configuration/models/configuration.model';
import { ConfigurationService } from '../../configuration/services/configuration.service';
import { Doctor } from '../../medical-staff/models/doctor.model';
import { MedicalStaffService } from '../../medical-staff/services/medical-staff.service';

interface FilaProfesional {
  medico: Doctor;
  dias: string;
  franja: string;
  intervalo: string;
  citasHoy: number;
}

const DIAS_CORTOS = ['', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']; // 1=Lunes ... 7=Domingo

// Panel del administrador: indicadores generales, profesionales con su horario y parámetros.
@Component({
  selector: 'app-panel-admin',
  imports: [RouterLink],
  templateUrl: './panel-admin.html',
  styleUrl: './panel-admin.scss',
})
export class PanelAdmin implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly citasApi = inject(AppointmentService);
  private readonly medicosApi = inject(MedicalStaffService);
  private readonly configuracionApi = inject(ConfigurationService);

  readonly hoy = fechaCompleta(hoyIso());

  readonly pacientes = signal<number | null>(null);
  readonly resumen = signal<AppointmentSummary | null>(null);
  readonly profesionales = signal<FilaProfesional[] | null>(null);
  readonly semanas = signal<number | null>(null);
  readonly error = signal('');

  readonly semana = computed(() => {
    const dias = this.resumen()?.week ?? [];
    const maximo = Math.max(1, ...dias.map((d) => d.count));
    return dias.map((d) => ({
      etiqueta: DIAS[aFecha(d.date).getDay()].slice(0, 3),
      total: d.count,
      alto: Math.round((d.count / maximo) * 100),
      esHoy: d.date === hoyIso(),
    }));
  });

  ngOnInit(): void {
    const fallo = (err: unknown) =>
      this.error.set(mensajeDeError(err as never, 'No se pudo cargar parte del resumen.'));

    this.http
      .get<{ total: number }>(`${API_BASE_URL}/patients/count`)
      .subscribe({ next: (r) => this.pacientes.set(r.total), error: fallo });
    this.citasApi.summary().subscribe({ next: (r) => this.resumen.set(r), error: fallo });
    this.configuracionApi
      .getGlobalConfiguration()
      .subscribe({ next: (c) => this.semanas.set(c.weeks), error: fallo });

    this.medicosApi
      .listDoctors()
      .pipe(
        switchMap((medicos) =>
          forkJoin({
            citas: this.citasApi.listByDate(hoyIso()),
            horarios: medicos.length
              ? forkJoin(medicos.map((m) => this.configuracionApi.getDoctorSchedule(m.doctorId)))
              : of([] as DoctorScheduleItem[][]),
          }).pipe(map(({ citas, horarios }) => ({ medicos, citas, horarios }))),
        ),
      )
      .subscribe({
        next: ({ medicos, citas, horarios }) =>
          this.profesionales.set(
            medicos.map((medico, i) => ({
              medico,
              ...this.describirHorario(horarios[i]),
              citasHoy: citas.filter(
                (c) => c.doctorId === medico.doctorId && c.status !== 'CANCELADA',
              ).length,
            })),
          ),
        error: (err) => {
          this.profesionales.set([]);
          fallo(err);
        },
      });
  }

  private describirHorario(
    horario: DoctorScheduleItem[],
  ): Pick<FilaProfesional, 'dias' | 'franja' | 'intervalo'> {
    if (!horario.length) {
      return { dias: 'Sin horario', franja: '—', intervalo: '—' };
    }
    const dias = [...horario]
      .sort((a, b) => a.dayOfWeek - b.dayOfWeek)
      .map((h) => DIAS_CORTOS[h.dayOfWeek]);
    const inicio = horario.map((h) => h.startTime).sort()[0];
    const fin = horario
      .map((h) => h.endTime)
      .sort()
      .at(-1)!;
    const intervalos = [...new Set(horario.map((h) => h.intervalMinutes))];
    return {
      dias: dias.join(', '),
      franja: `${horaAmPm(inicio)} – ${horaAmPm(fin)}`,
      intervalo: intervalos.map((m) => `${m} min`).join(' / '),
    };
  }
}
