// Formatos de fecha y hora en español, pensados para que los pacientes los lean sin esfuerzo:
// "Martes 13 de octubre", "9:00 a. m.".

export const DIAS = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
export const MESES = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
];

/** "2026-10-13" -> fecha local (sin desfase por zona horaria). */
export function aFecha(iso: string): Date {
  const [anio, mes, dia] = iso.slice(0, 10).split('-').map(Number);
  return new Date(anio, mes - 1, dia);
}

/** Fecha local -> "2026-10-13". */
export function aIso(fecha: Date): string {
  const mes = String(fecha.getMonth() + 1).padStart(2, '0');
  const dia = String(fecha.getDate()).padStart(2, '0');
  return `${fecha.getFullYear()}-${mes}-${dia}`;
}

export function hoyIso(): string {
  return aIso(new Date());
}

/** "Martes 13 de octubre" */
export function fechaLarga(iso: string): string {
  const fecha = aFecha(iso);
  return `${DIAS[fecha.getDay()]} ${fecha.getDate()} de ${MESES[fecha.getMonth()]}`;
}

/** "Martes 13 de octubre de 2026" */
export function fechaCompleta(iso: string): string {
  return `${fechaLarga(iso)} de ${aFecha(iso).getFullYear()}`;
}

/** "09:00", "09:00:00" o "14:30" -> "9:00 a. m." / "2:30 p. m." */
export function horaAmPm(hora: string): string {
  const [h, m] = hora.split(':').map(Number);
  const sufijo = h < 12 ? 'a. m.' : 'p. m.';
  const hora12 = h % 12 === 0 ? 12 : h % 12;
  return `${hora12}:${String(m).padStart(2, '0')} ${sufijo}`;
}
