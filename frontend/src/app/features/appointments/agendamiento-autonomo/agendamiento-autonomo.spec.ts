import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { API_BASE_URL } from '../../../core/api-config';
import { aIso } from '../../../shared/fechas';
import { Appointment, SchedulingOptions } from '../models/appointment.model';
import { AgendamientoAutonomo } from './agendamiento-autonomo';

const DIA = aIso(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000));
const ULTIMO_DIA = aIso(new Date(Date.now() + 28 * 24 * 60 * 60 * 1000));

function opciones(extra: Partial<SchedulingOptions> = {}): SchedulingOptions {
  return {
    services: [
      { serviceType: 'CONSULTA_GENERAL', label: 'Consulta General', specialty: 'Medicina General', allowed: true, lockedReason: null },
      { serviceType: 'FISIOTERAPIA', label: 'Fisioterapia', specialty: 'Fisioterapia', allowed: false, lockedReason: 'Requiere autorización médica de una Consulta General' },
    ],
    authorization: null,
    activeAppointment: null,
    windowWeeks: 4,
    lastBookableDate: ULTIMO_DIA,
    ...extra,
  };
}

const CITA: Appointment = {
  appointmentId: 30,
  patientId: 1,
  patientName: null,
  patientPhone: null,
  doctorId: 1,
  doctorName: 'Dra. Laura Muñoz',
  serviceType: 'CONSULTA_GENERAL',
  date: DIA,
  startTime: '09:30:00',
  endTime: '10:00:00',
  reason: 'Cita agendada por el paciente',
  status: 'AGENDADA',
};

describe('AgendamientoAutonomo', () => {
  let fixture: ComponentFixture<AgendamientoAutonomo>;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [AgendamientoAutonomo],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    fixture = TestBed.createComponent(AgendamientoAutonomo);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => http.verify());

  function pagina(): HTMLElement {
    fixture.detectChanges();
    return fixture.nativeElement as HTMLElement;
  }

  function botonConTexto(texto: string): HTMLButtonElement {
    const boton = [...pagina().querySelectorAll('button')].find((b) =>
      b.textContent!.includes(texto),
    );
    if (!boton) {
      throw new Error(`No hay un botón con el texto "${texto}"`);
    }
    return boton as HTMLButtonElement;
  }

  function responderOpciones(datos: SchedulingOptions): void {
    http.expectOne(`${API_BASE_URL}/appointments/me/options`).flush(datos);
  }

  it('blocks scheduling while the patient has an active appointment', () => {
    responderOpciones(opciones({ activeAppointment: CITA }));

    expect(pagina().textContent).toContain('Ya tienes una cita agendada');
    expect(pagina().querySelector('.pasos')).toBeNull();
  });

  it('only lets the patient pick the services she is allowed to book', () => {
    responderOpciones(opciones());

    expect(botonConTexto('Fisioterapia').disabled).toBe(true);
    expect(pagina().textContent).toContain('Requiere autorización médica');
    expect(botonConTexto('Siguiente').disabled).toBe(true);

    botonConTexto('Consulta General').click();
    expect(botonConTexto('Siguiente').disabled).toBe(false);
  });

  it('books the chosen slot and shows the confirmation', () => {
    responderOpciones(opciones());

    botonConTexto('Consulta General').click();
    botonConTexto('Siguiente').click();
    const profesionales = http.expectOne((r) => r.url === `${API_BASE_URL}/medical/doctors/available`);
    expect(profesionales.request.params.get('specialty')).toBe('Medicina General');
    profesionales.flush([
      { doctorId: 1, fullName: 'Dra. Laura Muñoz', specialty: 'Medicina General', nextAvailableDate: DIA },
    ]);

    botonConTexto('Dra. Laura Muñoz').click();
    botonConTexto('Siguiente').click();
    http
      .expectOne((r) => r.url === `${API_BASE_URL}/medical/availability/calendar`)
      .flush({ doctorId: 1, lastBookableDate: ULTIMO_DIA, days: [{ date: DIA, availableSlots: 2 }] });

    pagina().querySelector<HTMLButtonElement>('.calendario__dia.con-cupos')!.click();
    http.expectOne((r) => r.url === `${API_BASE_URL}/medical/availability`).flush({
      doctorId: 1,
      date: DIA,
      intervalMinutes: 30,
      slots: [
        { time: '09:00', available: false },
        { time: '09:30', available: true },
      ],
    });

    botonConTexto('--:--').click();
    expect(botonConTexto('Ocupado').disabled).toBe(true);
    botonConTexto('9:30 a. m.').click();
    botonConTexto('Siguiente').click();

    expect(pagina().textContent).toContain('9:30 a. m. – 10:00 a. m.');
    botonConTexto('Confirmar Cita').click();
    const reserva = http.expectOne(`${API_BASE_URL}/appointments/autonomous`);
    expect(reserva.request.body).toEqual({
      doctorId: 1,
      serviceType: 'CONSULTA_GENERAL',
      date: DIA,
      startTime: '09:30',
      reason: '',
    });
    reserva.flush(CITA);

    expect(pagina().textContent).toContain('¡Cita Agendada Exitosamente!');
    expect(pagina().textContent).toContain('Dra. Laura Muñoz');
  });

  it('goes back to pick another time when the slot was just taken', () => {
    responderOpciones(opciones());
    const componente = fixture.componentInstance;
    componente.servicio.set(opciones().services[0]);
    componente.profesional.set({ doctorId: 1, fullName: 'Dra. Laura Muñoz', specialty: 'Medicina General', nextAvailableDate: DIA });
    componente.fecha.set(DIA);
    componente.hora.set({ time: '09:30', available: true });
    componente.paso.set(3);

    botonConTexto('Confirmar Cita').click();
    http
      .expectOne(`${API_BASE_URL}/appointments/autonomous`)
      .flush(
        { message: 'Ese horario ya no está disponible. Por favor elige otro.' },
        { status: 409, statusText: 'Conflict' },
      );
    http.expectOne((r) => r.url === `${API_BASE_URL}/medical/availability/calendar`).flush({
      doctorId: 1,
      lastBookableDate: ULTIMO_DIA,
      days: [],
    });
    http.expectOne((r) => r.url === `${API_BASE_URL}/medical/availability`).flush({
      doctorId: 1,
      date: DIA,
      intervalMinutes: 30,
      slots: [],
    });

    expect(componente.paso()).toBe(2);
    expect(componente.hora()).toBeNull();
    expect(pagina().querySelector('[role="alert"]')?.textContent).toContain('Ese horario ya no está disponible');
  });
});
