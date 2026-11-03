import { Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ConfirmDialog } from '../../../ui/organisms/confirm-dialog/confirm-dialog';
import { CitaItem } from '../../../ui/organisms/cita-item/cita-item';
import { CitasDelPaciente } from '../citas-del-paciente';
import { Alert } from '../../../ui/atoms/alert/alert';
import { EmptyState } from '../../../ui/molecules/empty-state/empty-state';

// Todas las citas del paciente: las próximas (cancelables) y las anteriores.
@Component({
  selector: 'app-mis-citas',
  imports: [RouterLink, CitaItem, ConfirmDialog, Alert, EmptyState],
  providers: [CitasDelPaciente],
  template: `
    <div class="mis-citas">
      <h1>Mis Citas</h1>
      <p class="subtitle">Consulta tus citas programadas y las que ya pasaron.</p>

      @if (estado.aviso()) {
        <app-alert tono="ok">{{ estado.aviso() }}</app-alert>
      }
      @if (estado.error()) {
        <app-alert tono="error">{{ estado.error() }}</app-alert>
      }

      <section class="card bloque">
        <h2 class="bloque__titulo">Próximas</h2>
        @for (cita of estado.proximas(); track cita.appointmentId) {
          <app-cita-item
            [cita]="cita"
            [cancelable]="true"
            (cancelar)="estado.pedirCancelacion($event)"
          />
        } @empty {
          <app-empty-state>
            @if (estado.citas() === null) {
              Cargando tus citas...
            } @else {
              No tienes citas programadas.
              <a class="link" routerLink="/appointments/agendar">Agendar una cita</a>
            }
          </app-empty-state>
        }
      </section>

      <section class="card bloque">
        <h2 class="bloque__titulo">Anteriores</h2>
        @for (cita of estado.historial(); track cita.appointmentId) {
          <app-cita-item [cita]="cita" />
        } @empty {
          @if (estado.citas() !== null) {
            <app-empty-state>Aún no tienes citas anteriores.</app-empty-state>
          }
        }
      </section>
    </div>

    @if (estado.porCancelar()) {
      <app-confirm-dialog
        titulo="¿Cancelar tu cita?"
        [mensaje]="estado.mensajeCancelacion()"
        textoConfirmar="Sí, cancelar cita"
        textoCancelar="No, conservarla"
        [ocupado]="estado.cancelando()"
        (confirmar)="estado.confirmarCancelacion()"
        (cancelar)="estado.descartarCancelacion()"
      />
    }
  `,
  styleUrl: '../inicio/inicio.scss',
})
export class MisCitas implements OnInit {
  readonly estado = inject(CitasDelPaciente);

  ngOnInit(): void {
    this.estado.cargar();
  }
}
