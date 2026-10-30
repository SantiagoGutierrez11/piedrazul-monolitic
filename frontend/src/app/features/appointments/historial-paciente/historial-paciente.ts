import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subject, catchError, debounceTime, of, switchMap } from 'rxjs';
import { mensajeDeError } from '../../../shared/error-messages';
import { DIAS, MESES, aFecha, horaAmPm } from '../../../shared/fechas';
import { Appointment, SERVICE_LABELS, STATUS_LABELS } from '../models/appointment.model';
import {
  COLUMNAS_HISTORIAL,
  MIN_DIGITOS_SUGERENCIAS,
  errorDeFormato,
  errorParaBuscar,
  masRecientePrimero,
  sugerirDesde,
} from './historial-paciente.reglas';
import { HistorialPacienteService, PacienteEncontrado } from './historial-paciente.service';

// Espera entre teclas antes de pedir sugerencias, para no consultar el backend con cada dígito.
export const ESPERA_SUGERENCIAS_MS = 250;

/** Mensajes de estado vacío de la pantalla (subtarea 1.4). */
export const MENSAJES_HISTORIAL = {
  inicio: 'Escribe la cédula del paciente para consultar su historial de citas.',
  pocosDigitos: (minimo: number) => `Escribe al menos ${minimo} dígitos para ver sugerencias.`,
  noEncontrado: (cedula: string) =>
    `No encontramos un paciente registrado con la cédula ${cedula}. Revisa el número e intenta de nuevo.`,
  sinCitas: (nombre: string) => `${nombre} no tiene citas registradas en Piedrazul.`,
  errorBusqueda: 'No se pudo buscar el paciente. Intenta de nuevo en unos minutos.',
  errorHistorial: 'No se pudo cargar el historial de citas. Intenta de nuevo en unos minutos.',
} as const;

/** "Mar 3 nov 2026": fecha corta para que la columna quepa en una línea. */
export function fechaCorta(iso: string): string {
  const fecha = aFecha(iso);
  const dia = DIAS[fecha.getDay()].slice(0, 3);
  return `${dia} ${fecha.getDate()} ${MESES[fecha.getMonth()].slice(0, 3)} ${fecha.getFullYear()}`;
}

/** Parte de la cédula que coincide con lo escrito, para resaltarla en la sugerencia. */
export function resaltar(documento: string, escrito: string): { coincide: string; resto: string } {
  return documento.startsWith(escrito)
    ? { coincide: escrito, resto: documento.slice(escrito.length) }
    : { coincide: '', resto: documento };
}

// Historial de citas de un paciente buscado por cédula (E7-HU1), para el médico, el agendador
// y el administrador.
@Component({
  selector: 'app-historial-paciente',
  templateUrl: './historial-paciente.html',
  styleUrl: './historial-paciente.scss',
})
export class HistorialPaciente {
  private readonly api = inject(HistorialPacienteService);

  readonly horaAmPm = horaAmPm;
  readonly fechaCorta = fechaCorta;
  readonly servicios = SERVICE_LABELS;
  readonly estados = STATUS_LABELS;
  readonly mensajes = MENSAJES_HISTORIAL;
  readonly minDigitos = MIN_DIGITOS_SUGERENCIAS;
  readonly columnas = COLUMNAS_HISTORIAL;
  readonly resaltar = resaltar;

  readonly cedula = signal('');
  readonly listaAbierta = signal(false);
  readonly activa = signal(-1); // sugerencia marcada con el teclado
  readonly sugerencias = signal<PacienteEncontrado[]>([]);
  readonly buscandoSugerencias = signal(false);
  readonly buscando = signal(false); // búsqueda exacta (botón Buscar)
  readonly paciente = signal<PacienteEncontrado | null>(null);
  readonly citas = signal<Appointment[] | null>(null); // null mientras carga el historial
  readonly noEncontrada = signal(''); // cédula buscada sin resultado
  readonly errorCedula = signal<string | null>(null); // formato inválido (subtarea 2.1)
  readonly error = signal(''); // fallo del backend

  readonly mostrarLista = computed(() => this.listaAbierta() && sugerirDesde(this.cedula()));

  // Cada cambio de la cédula pide sugerencias; switchMap descarta la respuesta de una
  // consulta vieja si el usuario siguió escribiendo.
  private readonly escritura = new Subject<string>();

  constructor() {
    this.escritura
      .pipe(
        debounceTime(ESPERA_SUGERENCIAS_MS),
        switchMap((texto) =>
          sugerirDesde(texto) ? this.api.buscar(texto).pipe(catchError(() => of([]))) : of([]),
        ),
        takeUntilDestroyed(),
      )
      .subscribe((pacientes) => {
        this.sugerencias.set(pacientes);
        this.buscandoSugerencias.set(false);
      });
  }

  escribir(valor: string): void {
    const escrito = valor.trim();
    this.cedula.set(escrito);
    this.errorCedula.set(errorDeFormato(escrito));
    this.listaAbierta.set(true);
    this.activa.set(-1);
    this.noEncontrada.set('');
    this.error.set('');
    // Mientras llega la respuesta la lista dice "Buscando pacientes..." y no "Ningún paciente".
    this.buscandoSugerencias.set(sugerirDesde(escrito));
    if (!sugerirDesde(escrito)) {
      this.sugerencias.set([]);
    }
    this.escritura.next(escrito);
  }

  teclear(evento: KeyboardEvent): void {
    const total = this.sugerencias().length;
    switch (evento.key) {
      case 'ArrowDown':
        evento.preventDefault();
        this.listaAbierta.set(true);
        this.activa.set(total === 0 ? -1 : (this.activa() + 1) % total);
        break;
      case 'ArrowUp':
        evento.preventDefault();
        this.activa.set(total === 0 ? -1 : (this.activa() - 1 + total) % total);
        break;
      case 'Enter':
        evento.preventDefault();
        if (this.mostrarLista() && this.activa() >= 0) {
          this.elegir(this.sugerencias()[this.activa()]);
        } else {
          this.buscar();
        }
        break;
      case 'Escape':
        this.listaAbierta.set(false);
        break;
    }
  }

  /** Muestra la ficha del paciente y carga su historial (subtarea 3.4). */
  elegir(paciente: PacienteEncontrado): void {
    this.cedula.set(paciente.documentNumber);
    this.errorCedula.set(null);
    this.paciente.set(paciente);
    this.noEncontrada.set('');
    this.error.set('');
    this.listaAbierta.set(false);
    this.activa.set(-1);

    this.citas.set(null);
    this.api.historial(paciente.patientId).subscribe({
      next: (citas) => this.citas.set(masRecientePrimero(citas)),
      error: (err: HttpErrorResponse) => {
        this.citas.set([]);
        this.error.set(mensajeDeError(err, MENSAJES_HISTORIAL.errorHistorial));
      },
    });
  }

  /** Botón Buscar o Enter sin sugerencia marcada: busca la cédula exacta (subtarea 3.3). */
  buscar(): void {
    const escrito = this.cedula();
    if (!escrito) {
      return;
    }
    const errorFormato = errorParaBuscar(escrito);
    if (errorFormato) {
      this.errorCedula.set(errorFormato);
      this.listaAbierta.set(false);
      return;
    }

    this.listaAbierta.set(false);
    this.error.set('');
    this.buscando.set(true);
    this.api.buscar(escrito).subscribe({
      next: (pacientes) => {
        this.buscando.set(false);
        const exacto = pacientes.find((p) => p.documentNumber === escrito);
        if (exacto) {
          this.elegir(exacto);
          return;
        }
        this.paciente.set(null);
        this.citas.set(null);
        this.noEncontrada.set(escrito);
      },
      error: (err: HttpErrorResponse) => {
        this.buscando.set(false);
        this.error.set(mensajeDeError(err, MENSAJES_HISTORIAL.errorBusqueda));
      },
    });
  }

  limpiar(): void {
    this.cedula.set('');
    this.errorCedula.set(null);
    this.sugerencias.set([]);
    this.paciente.set(null);
    this.citas.set(null);
    this.noEncontrada.set('');
    this.error.set('');
    this.listaAbierta.set(false);
    this.escritura.next('');
  }
}
