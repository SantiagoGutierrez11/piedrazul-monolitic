import { Component, computed, signal } from '@angular/core';
import { DIAS, MESES, aFecha, horaAmPm } from '../../../shared/fechas';
import { Appointment, SERVICE_LABELS, STATUS_LABELS } from '../models/appointment.model';
import {
  CITAS_DE_MUESTRA,
  PACIENTES_DE_MUESTRA,
  PacienteEncontrado,
} from './historial-paciente.muestra';

// Valores provisionales del diseño; las reglas definitivas se fijan en la subtarea 2.1.
const MIN_DIGITOS_SUGERENCIAS = 3;
const MAX_SUGERENCIAS = 8;

/** Mensajes de estado vacío de la pantalla (subtarea 1.4). */
export const MENSAJES_HISTORIAL = {
  inicio: 'Escribe la cédula del paciente para consultar su historial de citas.',
  pocosDigitos: (minimo: number) => `Escribe al menos ${minimo} dígitos para ver sugerencias.`,
  noEncontrado: (cedula: string) =>
    `No encontramos un paciente registrado con la cédula ${cedula}. Revisa el número e intenta de nuevo.`,
  sinCitas: (nombre: string) => `${nombre} no tiene citas registradas en Piedrazul.`,
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

// Historial de citas de un paciente buscado por cédula (E7-HU1), para el médico y el agendador.
@Component({
  selector: 'app-historial-paciente',
  templateUrl: './historial-paciente.html',
  styleUrl: './historial-paciente.scss',
})
export class HistorialPaciente {
  readonly horaAmPm = horaAmPm;
  readonly fechaCorta = fechaCorta;
  readonly servicios = SERVICE_LABELS;
  readonly estados = STATUS_LABELS;
  readonly mensajes = MENSAJES_HISTORIAL;
  readonly minDigitos = MIN_DIGITOS_SUGERENCIAS;
  readonly resaltar = resaltar;

  readonly cedula = signal('');
  readonly listaAbierta = signal(false);
  readonly activa = signal(-1); // sugerencia marcada con el teclado
  readonly paciente = signal<PacienteEncontrado | null>(null);
  readonly noEncontrada = signal(''); // cédula buscada sin resultado

  readonly sugerencias = computed(() => {
    const escrito = this.cedula();
    if (escrito.length < MIN_DIGITOS_SUGERENCIAS) {
      return [];
    }
    return PACIENTES_DE_MUESTRA.filter((p) => p.documentNumber.startsWith(escrito)).slice(
      0,
      MAX_SUGERENCIAS,
    );
  });

  readonly mostrarLista = computed(
    () => this.listaAbierta() && this.cedula().length >= MIN_DIGITOS_SUGERENCIAS,
  );

  // Más reciente primero (la regla definitiva se fija en la subtarea 2.2).
  readonly citas = computed<Appointment[]>(() => {
    const paciente = this.paciente();
    if (!paciente) {
      return [];
    }
    return CITAS_DE_MUESTRA.filter((c) => c.patientId === paciente.patientId).sort((a, b) =>
      (b.date + b.startTime).localeCompare(a.date + a.startTime),
    );
  });

  escribir(valor: string): void {
    this.cedula.set(valor.trim());
    this.listaAbierta.set(true);
    this.activa.set(-1);
    this.noEncontrada.set('');
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

  elegir(paciente: PacienteEncontrado): void {
    this.cedula.set(paciente.documentNumber);
    this.paciente.set(paciente);
    this.noEncontrada.set('');
    this.listaAbierta.set(false);
    this.activa.set(-1);
  }

  /** Botón Buscar o Enter sin sugerencia marcada: busca la cédula exacta. */
  buscar(): void {
    const escrito = this.cedula();
    if (!escrito) {
      return;
    }
    const exacto = PACIENTES_DE_MUESTRA.find((p) => p.documentNumber === escrito);
    if (exacto) {
      this.elegir(exacto);
      return;
    }
    this.paciente.set(null);
    this.listaAbierta.set(false);
    this.noEncontrada.set(escrito);
  }

  limpiar(): void {
    this.cedula.set('');
    this.paciente.set(null);
    this.noEncontrada.set('');
    this.listaAbierta.set(false);
  }
}
