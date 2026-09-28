import { Appointment } from '../appointments/models/appointment.model';

/** Una cita es "próxima" mientras esté activa y no haya pasado su día. */
export function esProxima(cita: Appointment, hoy: string): boolean {
  return (cita.status === 'AGENDADA' || cita.status === 'REAGENDADA') && cita.date >= hoy;
}

/** Próximas en orden cronológico; el historial, de la más reciente a la más antigua. */
export function separarCitas(citas: Appointment[], hoy: string) {
  const clave = (cita: Appointment) => `${cita.date}T${cita.startTime}`;
  const proximas = citas
    .filter((cita) => esProxima(cita, hoy))
    .sort((a, b) => clave(a).localeCompare(clave(b)));
  const historial = citas
    .filter((cita) => !esProxima(cita, hoy))
    .sort((a, b) => clave(b).localeCompare(clave(a)));
  return { proximas, historial };
}
