import { Component, OnInit, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';
import { ConfirmDialog } from '../../../shared/confirm-dialog/confirm-dialog';
import { fechaCompleta, fechaLarga, horaAmPm, hoyIso } from '../../../shared/fechas';
import { SERVICE_LABELS } from '../../appointments/models/appointment.model';
import { CitaItem } from '../cita-item/cita-item';
import { CitasDelPaciente } from '../citas-del-paciente';

const CITAS_EN_HISTORIAL = 5;

// Pantalla principal del paciente: próxima cita, historial reciente y acceso al agendamiento.
@Component({
  selector: 'app-inicio-paciente',
  imports: [RouterLink, CitaItem, ConfirmDialog],
  providers: [CitasDelPaciente],
  templateUrl: './inicio.html',
  styleUrl: './inicio.scss',
})
export class InicioPaciente implements OnInit {
  private readonly auth = inject(AuthService);
  readonly estado = inject(CitasDelPaciente);

  readonly fechaLarga = fechaLarga;
  readonly horaAmPm = horaAmPm;
  readonly servicios = SERVICE_LABELS;
  readonly hoy = fechaCompleta(hoyIso());

  readonly nombre = computed(() => this.auth.user()?.fullName.split(' ')[0] ?? '');
  readonly proxima = computed(() => this.estado.proximas()[0] ?? null);
  readonly historial = computed(() => this.estado.historial().slice(0, CITAS_EN_HISTORIAL));

  ngOnInit(): void {
    this.estado.cargar();
  }
}
