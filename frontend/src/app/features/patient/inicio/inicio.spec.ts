import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { signal } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { API_BASE_URL } from '../../../core/api-config';
import { AuthService } from '../../../core/auth/auth.service';
import { aIso } from '../../../shared/fechas';
import { Appointment } from '../../appointments/models/appointment.model';
import { InicioPaciente } from './inicio';

const MIS_CITAS = `${API_BASE_URL}/appointments/me`;
const dias = (n: number) => aIso(new Date(Date.now() + n * 24 * 60 * 60 * 1000));

function cita(id: number, fecha: string, status: Appointment['status'], doctor = 'Dra. Laura Muñoz'): Appointment {
  return {
    appointmentId: id,
    patientId: 1,
    patientName: null,
    patientPhone: null,
    doctorId: 1,
    doctorName: doctor,
    serviceType: 'CONSULTA_GENERAL',
    date: fecha,
    startTime: '09:00:00',
    endTime: '09:30:00',
    reason: 'Control general',
    status,
  };
}

describe('InicioPaciente', () => {
  let fixture: ComponentFixture<InicioPaciente>;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [InicioPaciente],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        {
          provide: AuthService,
          useValue: {
            user: signal({ id: 'u1', email: 'x', fullName: 'María García', roles: ['paciente'] }),
          },
        },
      ],
    });
    fixture = TestBed.createComponent(InicioPaciente);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  function pagina(): HTMLElement {
    fixture.detectChanges();
    return fixture.nativeElement as HTMLElement;
  }

  it('greets the patient and shows her next appointment and history', () => {
    http.expectOne(MIS_CITAS).flush([
      cita(1, dias(-10), 'ATENDIDA', 'Dr. Juan Pérez'),
      cita(2, dias(5), 'AGENDADA'),
      cita(3, dias(-20), 'CANCELADA'),
    ]);

    const texto = pagina().textContent!;
    expect(texto).toContain('Hola, María');
    expect(pagina().querySelector('.proxima')!.textContent).toContain('Dra. Laura Muñoz');
    const historial = [...pagina().querySelectorAll('app-cita-item')].map((item) => item.textContent);
    expect(historial.length).toBe(2);
    expect(historial[0]).toContain('Dr. Juan Pérez');
    expect(historial[1]).toContain('Cancelada');
  });

  it('invites to book when there is no upcoming appointment', () => {
    http.expectOne(MIS_CITAS).flush([]);

    expect(pagina().textContent).toContain('No tienes citas programadas');
  });

  it('cancels the next appointment after confirming', () => {
    http.expectOne(MIS_CITAS).flush([cita(2, dias(5), 'AGENDADA')]);

    pagina().querySelector<HTMLButtonElement>('.proxima .cancelar')!.click();
    expect(pagina().querySelector('[role="alertdialog"]')!.textContent).toContain('quedará cancelada');

    [...pagina().querySelectorAll('[role="alertdialog"] button')]
      .find((b) => b.textContent!.includes('Sí, cancelar cita'))!
      .dispatchEvent(new Event('click'));
    http.expectOne(`${API_BASE_URL}/appointments/me/2/cancel`).flush(cita(2, dias(5), 'CANCELADA'));
    http.expectOne(MIS_CITAS).flush([cita(2, dias(5), 'CANCELADA')]);

    expect(pagina().textContent).toContain('Tu cita fue cancelada.');
    expect(pagina().querySelector('[role="alertdialog"]')).toBeNull();
    expect(pagina().textContent).toContain('No tienes citas programadas');
  });
});
