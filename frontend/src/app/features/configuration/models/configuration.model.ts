export interface GlobalConfiguration {
  weeks: number;
}

export interface DoctorScheduleItem {
  dayOfWeek: number; // 1=Lunes ... 7=Domingo
  startTime: string;
  endTime: string;
  intervalMinutes: number;
}
