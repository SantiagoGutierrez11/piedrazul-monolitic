// Debe coincidir con el JSON que devuelve backend/app/modules/appointment/api/routes.py.

export type ServiceType = 'CONSULTA_GENERAL' | 'FISIOTERAPIA' | 'QUIROPRAXIA' | 'TERAPIA_NEURAL';
export type AppointmentStatus = 'AGENDADA' | 'REAGENDADA' | 'ATENDIDA' | 'CANCELADA';

export const SERVICE_LABELS: Record<ServiceType, string> = {
  CONSULTA_GENERAL: 'Consulta General',
  FISIOTERAPIA: 'Fisioterapia',
  QUIROPRAXIA: 'Quiropraxia',
  TERAPIA_NEURAL: 'Terapia Neural',
};

export const STATUS_LABELS: Record<AppointmentStatus, string> = {
  AGENDADA: 'Agendada',
  REAGENDADA: 'Reagendada',
  ATENDIDA: 'Atendida',
  CANCELADA: 'Cancelada',
};

export interface Appointment {
  appointmentId: number;
  patientId: number;
  patientName: string | null;
  patientPhone: string | null;
  doctorId: number;
  doctorName: string;
  serviceType: ServiceType;
  date: string; // ISO yyyy-MM-dd
  startTime: string; // HH:mm:ss
  endTime: string;
  reason: string;
  notes?: string;
  status: AppointmentStatus;
}

// GET /appointments/summary: indicadores de los paneles del agendador y el administrador.
export interface AppointmentSummary {
  today: number;
  pending: number;
  week: { date: string; count: number }[];
}

// Cuerpo de POST /appointments/autonomous: el paciente sale del token, no se envía.
export interface PatientBookingRequest {
  doctorId: number;
  serviceType: ServiceType;
  date: string;
  startTime: string; // HH:mm
  reason: string;
}

export interface ServiceOption {
  serviceType: ServiceType;
  label: string;
  specialty: string;
  allowed: boolean;
  lockedReason: string | null;
}

export interface SchedulingOptions {
  services: ServiceOption[];
  authorization: { serviceType: ServiceType; label: string; expiresAt: string } | null;
  activeAppointment: Appointment | null;
  windowWeeks: number;
  lastBookableDate: string;
}
