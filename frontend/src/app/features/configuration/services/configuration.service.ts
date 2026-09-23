import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { API_BASE_URL } from '../../../core/api-config';
import { DoctorScheduleItem, GlobalConfiguration } from '../models/configuration.model';

@Injectable({ providedIn: 'root' })
export class ConfigurationService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${API_BASE_URL}/configuration`;

  getGlobalConfiguration() {
    return this.http.get<GlobalConfiguration>(`${this.baseUrl}/global`);
  }

  updateAppointmentWindow(weeks: number) {
    return this.http.put(`${this.baseUrl}/global/appointment-window`, { weeks });
  }

  getDoctorSchedule(doctorId: number) {
    return this.http.get<DoctorScheduleItem[]>(`${this.baseUrl}/doctor/${doctorId}/schedule`);
  }

  updateDoctorSchedule(doctorId: number, schedules: DoctorScheduleItem[]) {
    return this.http.put(`${this.baseUrl}/doctor/${doctorId}/schedule`, { schedules });
  }
}
