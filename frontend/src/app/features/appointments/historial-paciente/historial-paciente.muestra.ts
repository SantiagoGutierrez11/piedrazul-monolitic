// Datos de muestra para revisar el diseño de la pantalla (subtareas 1.1 a 1.4).
// Se reemplazan por la búsqueda y el historial reales del backend en las subtareas 3.3 y 3.4.
import { Appointment } from '../models/appointment.model';

export interface PacienteEncontrado {
  patientId: number;
  fullName: string;
  documentType: string;
  documentNumber: string;
  phone: string | null;
}

export const PACIENTES_DE_MUESTRA: PacienteEncontrado[] = [
  { patientId: 1, fullName: 'María García López', documentType: 'CC', documentNumber: '1061234567', phone: '+57 300 123 4567' },
  { patientId: 2, fullName: 'Carlos Rodríguez', documentType: 'CC', documentNumber: '1061234890', phone: '+57 310 987 6543' },
  { patientId: 3, fullName: 'Laura Sánchez', documentType: 'CC', documentNumber: '1062345678', phone: '+57 320 456 7890' },
  { patientId: 4, fullName: 'Andrés Gómez', documentType: 'CC', documentNumber: '94512345', phone: '+57 305 666 7788' },
];

function cita(
  id: number,
  patientId: number,
  date: string,
  hora: string,
  doctorName: string,
  serviceType: Appointment['serviceType'],
  status: Appointment['status'],
): Appointment {
  return {
    appointmentId: id,
    patientId,
    patientName: null,
    patientPhone: null,
    doctorId: 1,
    doctorName,
    serviceType,
    date,
    startTime: `${hora}:00`,
    endTime: `${hora}:30`,
    reason: '',
    status,
  };
}

// Laura Sánchez (paciente 3) no tiene citas: sirve para ver el mensaje "sin citas registradas".
export const CITAS_DE_MUESTRA: Appointment[] = [
  cita(1, 1, '2026-11-03', '10:30', 'Dra. Laura Muñoz', 'CONSULTA_GENERAL', 'AGENDADA'),
  cita(2, 1, '2026-10-19', '11:30', 'Dra. Laura Muñoz', 'CONSULTA_GENERAL', 'ATENDIDA'),
  cita(3, 1, '2026-09-24', '08:00', 'Dr. Juan Pérez', 'FISIOTERAPIA', 'ATENDIDA'),
  cita(4, 1, '2026-09-10', '09:00', 'Dr. Juan Pérez', 'FISIOTERAPIA', 'CANCELADA'),
  cita(5, 1, '2026-08-21', '08:30', 'Dra. Laura Muñoz', 'CONSULTA_GENERAL', 'ATENDIDA'),
  cita(6, 2, '2026-10-28', '09:00', 'Dra. Ana Soto', 'QUIROPRAXIA', 'REAGENDADA'),
  cita(7, 2, '2026-10-02', '08:00', 'Dra. Laura Muñoz', 'CONSULTA_GENERAL', 'ATENDIDA'),
  cita(8, 4, '2026-10-30', '10:00', 'Dra. Laura Muñoz', 'CONSULTA_GENERAL', 'AGENDADA'),
];
