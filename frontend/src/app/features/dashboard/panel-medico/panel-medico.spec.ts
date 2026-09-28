import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { API_BASE_URL } from '../../../core/api-config';
import { hoyIso } from '../../../shared/fechas';
import { Appointment } from '../../appointments/models/appointment.model';
import { PanelMedico } from './panel-medico';

function cita(id: number, hora: string, status: Appointment['status']): Appointment {
  return {
    appointmentId: id,
    patientId: id,
    patientName: `Paciente ${id}`,
    patientPhone: null,
    doctorId: 1,
    doctorName: 'Dra. Laura Muñoz',
    serviceType: 'CONSULTA_GENERAL',
    date: hoyIso(),
    startTime: `${hora}:00`,
    endTime: `${hora}:30`,
    reason: 'Control',
    status,
  };
}

describe('PanelMedico', () => {
  it('summarizes the day and lists free slots of the doctor schedule', () => {
    TestBed.configureTestingModule({
      imports: [PanelMedico],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    const fixture = TestBed.createComponent(PanelMedico);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();

    http
      .expectOne(`${API_BASE_URL}/medical/doctors/me`)
      .flush({ doctorId: 1, fullName: 'Dra. Laura Muñoz', specialty: 'Medicina General' });
    http
      .expectOne(`${API_BASE_URL}/appointments/doctor/1/date/${hoyIso()}`)
      .flush([cita(1, '08:00', 'ATENDIDA'), cita(2, '08:30', 'AGENDADA'), cita(3, '09:00', 'CANCELADA')]);
    http
      .expectOne((req) => req.url === `${API_BASE_URL}/medical/availability`)
      .flush({
        doctorId: 1,
        date: hoyIso(),
        intervalMinutes: 30,
        slots: ['08:00', '08:30', '09:00'].map((time) => ({ time, available: time === '09:00' })),
      });
    fixture.detectChanges();

    const panel = fixture.componentInstance;
    expect(panel.total()).toBe(2);
    expect(panel.atendidas()).toBe(1);
    expect(panel.proxima()?.appointmentId).toBe(2);
    expect(panel.agenda().map((f) => f.cita?.appointmentId ?? null)).toEqual([1, 2, null]);
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Disponible');
  });
});
