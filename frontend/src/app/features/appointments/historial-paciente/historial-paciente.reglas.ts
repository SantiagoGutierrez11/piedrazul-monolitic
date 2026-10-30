// Reglas de la búsqueda por cédula y del historial (E7-HU1, subtareas 2.1 a 2.3).
// Son las mismas del backend: app/modules/patient/application/document_search.py y
// app/modules/appointment/application/patient_history.py.
import { Role } from '../../../core/auth/auth.models';
import { Appointment } from '../models/appointment.model';

// ---- 2.1 Formato de la cédula y autocompletado

export const MIN_DIGITOS = 5;
export const MAX_DIGITOS = 10;
export const MIN_DIGITOS_SUGERENCIAS = 3;
export const MAX_SUGERENCIAS = 8;

export const ERRORES_CEDULA = {
  formato: 'La cédula solo puede tener números, sin puntos, letras ni espacios.',
  larga: `La cédula tiene como máximo ${MAX_DIGITOS} dígitos.`,
  corta: `Escribe la cédula completa: tiene al menos ${MIN_DIGITOS} dígitos.`,
} as const;

/** Error de formato mientras se escribe, o `null` si lo escrito puede ser una cédula. */
export function errorDeFormato(texto: string): string | null {
  if (texto === '') {
    return null;
  }
  if (!/^\d+$/.test(texto)) {
    return ERRORES_CEDULA.formato;
  }
  return texto.length > MAX_DIGITOS ? ERRORES_CEDULA.larga : null;
}

/** Error al pulsar Buscar (búsqueda exacta), o `null` si la cédula está completa. */
export function errorParaBuscar(texto: string): string | null {
  return errorDeFormato(texto) ?? (texto.length < MIN_DIGITOS ? ERRORES_CEDULA.corta : null);
}

export function sugerirDesde(texto: string): boolean {
  return errorDeFormato(texto) === null && texto.length >= MIN_DIGITOS_SUGERENCIAS;
}

// ---- 2.2 Orden y datos del historial

/** Columnas de la tabla; el historial incluye citas futuras, atendidas y canceladas. */
export const COLUMNAS_HISTORIAL = ['Fecha', 'Hora', 'Profesional', 'Servicio', 'Estado'] as const;

/** De la cita más reciente a la más antigua; el mismo día, la de hora más tarde primero. */
export function masRecientePrimero(citas: Appointment[]): Appointment[] {
  return [...citas].sort((a, b) => (b.date + b.startTime).localeCompare(a.date + a.startTime));
}

// ---- 2.3 Roles

/** Médico (o terapista), agendador y administrador. El paciente ve solo las suyas en "Mis citas". */
export const ROLES_HISTORIAL: Role[] = ['medico', 'agendador', 'administrador'];
