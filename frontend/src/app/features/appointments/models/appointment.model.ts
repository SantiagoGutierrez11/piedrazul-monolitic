// Debe coincidir con el JSON que devuelve backend/app/modules/appointment/api/routes.py.

export type ServiceType = 'CONSULTA_GENERAL' | 'FISIOTERAPIA' | 'QUIROPRAXIA' | 'TERAPIA_NEURAL';
export type AppointmentStatus = 'AGENDADA' | 'REAGENDADA' | 'ATENDIDA' | 'CANCELADA';

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

export interface CreateAppointmentRequest {
  patientId: number;
  doctorId: number;
  doctorName: string;
  serviceType: ServiceType;
  date: string;
  startTime: string;
  endTime: string;
  reason: string;
  notes?: string;
}
