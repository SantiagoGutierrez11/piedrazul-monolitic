// Debe coincidir con el JSON que devuelve
// backend/app/modules/medical_staff/api/routes.py.

export interface Doctor {
  doctorId: number;
  fullName: string;
  specialty: string;
}

export interface AvailableDoctor extends Doctor {
  // Primera fecha con cupo dentro de la ventana de agendamiento; null si no hay.
  nextAvailableDate: string | null;
}

export interface Slot {
  time: string; // HH:mm
  available: boolean;
}

export interface DayAvailability {
  doctorId: number;
  date: string;
  intervalMinutes: number | null;
  slots: Slot[];
}

export interface AvailabilityCalendar {
  doctorId: number;
  lastBookableDate: string;
  days: { date: string; availableSlots: number }[];
}
