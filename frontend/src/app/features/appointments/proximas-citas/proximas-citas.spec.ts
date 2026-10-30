import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { API_BASE_URL } from '../../../core/api-config';
import { Role } from '../../../core/auth/auth.models';
import { AuthService } from '../../../core/auth/auth.service';
import { Appointment, UpcomingAppointments } from '../models/appointment.model';
import { ProximasCitas, etiquetaSemana, rangoSemana } from './proximas-citas';

const UPCOMING = `${API_BASE_URL}/appointments/upcoming`;

function cita(id: number, date: string, hora: string): Appointment {
  return {
    appointmentId: id,
    patientId: id,
    patientName: `Paciente ${id}`,
    patientPhone: null,
    patientDocument: `CC 106123456${id}`,
    doctorId: 1,
    doctorName: 'Dra. Laura Muñoz',
    serviceType: 'CONSULTA_GENERAL',
    date,
    startTime: `${hora}:00`,
    endTime: `${hora}:30`,
    reason: 'Control',
    status: 'AGENDADA',
  };
}

const REPORTE: UpcomingAppointments = {
  dateFrom: '2026-10-16',
  dateTo: '2026-10-25',
  total: 3,
  weeks: [
    {
      start: '2026-10-12',
      end: '2026-10-18',
      total: 1,
      appointments: [cita(1, '2026-10-16', '08:00')],
    },
    {
      start: '2026-10-19',
      end: '2026-10-25',
      total: 2,
      appointments: [cita(2, '2026-10-21', '10:30'), cita(3, '2026-10-21', '11:00')],
    },
  ],
};

function render(roles: Role[]) {
  TestBed.configureTestingModule({
    imports: [ProximasCitas],
    providers: [
      provideHttpClient(),
      provideHttpClientTesting(),
      {
        provide: AuthService,
        useValue: { hasRole: (...allowed: Role[]) => allowed.some((role) => roles.includes(role)) },
      },
    ],
  });
  const fixture = TestBed.createComponent(ProximasCitas);
  const http = TestBed.inject(HttpTestingController);
  fixture.detectChanges();
  return { fixture, http, page: fixture.nativeElement as HTMLElement };
}

describe('ProximasCitas', () => {
  it('shows the scheduler every professional, week by week', () => {
    const { fixture, http, page } = render(['agendador']);
    http.expectOne(`${API_BASE_URL}/medical/doctors`).flush([]);
    http.expectOne((req) => req.url === UPCOMING && req.params.get('weeks') === '4').flush(REPORTE);
    fixture.detectChanges();

    const panel = fixture.componentInstance;
    expect(panel.estaSemana()).toBe(1);
    expect(panel.semanaPico()?.rango).toBe('19 al 25 de octubre');
    expect(panel.vista()[1].dias).toEqual([
      diaConCitas('2026-10-21', 'Miércoles 21 de octubre', [2, 3]),
    ]);
    expect(page.textContent).toContain('Próxima semana');
    expect(page.querySelector('thead')!.textContent).toContain('Profesional');
    expect(page.querySelector('thead')!.textContent).toContain('Cédula');
    expect(page.textContent).toContain('CC 1061234561');
  });

  it('asks for a single professional when the scheduler picks one', () => {
    const { fixture, http } = render(['administrador']);
    http.expectOne(`${API_BASE_URL}/medical/doctors`).flush([]);
    http.expectOne(UPCOMING + '?weeks=4').flush(REPORTE);

    fixture.componentInstance.cambiarMedico('2');

    const request = http.expectOne((req) => req.url === UPCOMING);
    expect(request.request.params.get('doctor_id')).toBe('2');
  });

  it('shows the doctor only their own agenda, without choosing a professional', () => {
    const { fixture, http, page } = render(['medico']);
    http.expectNone(`${API_BASE_URL}/medical/doctors`);
    http.expectOne((req) => req.url === UPCOMING).flush(REPORTE);
    fixture.detectChanges();

    expect(page.textContent).not.toContain('Todos los profesionales');
    expect(page.querySelector('thead')!.textContent).not.toContain('Profesional');
  });
});

describe('week labels', () => {
  it('names the weeks relative to the current one', () => {
    expect([0, 1, 3].map(etiquetaSemana)).toEqual(['Esta semana', 'Próxima semana', 'En 3 semanas']);
  });

  it('writes the month once when the week does not change month', () => {
    expect(rangoSemana('2026-10-12', '2026-10-18')).toBe('12 al 18 de octubre');
    expect(rangoSemana('2026-10-26', '2026-11-01')).toBe('26 de octubre al 1 de noviembre');
  });
});

function diaConCitas(fecha: string, titulo: string, ids: number[]) {
  return {
    fecha,
    titulo,
    citas: ids.map((id) => expect.objectContaining({ appointmentId: id })),
  };
}
