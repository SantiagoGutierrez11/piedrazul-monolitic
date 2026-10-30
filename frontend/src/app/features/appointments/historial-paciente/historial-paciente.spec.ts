import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { API_BASE_URL } from '../../../core/api-config';
import { Appointment } from '../models/appointment.model';
import {
  ESPERA_SUGERENCIAS_MS,
  HistorialPaciente,
  fechaCorta,
  resaltar,
} from './historial-paciente';
import { PacienteEncontrado } from './historial-paciente.service';

const BUSQUEDA = `${API_BASE_URL}/patients/search`;
const historialDe = (id: number) => `${API_BASE_URL}/appointments/patient/${id}/history`;

const MARIA: PacienteEncontrado = {
  patientId: 1,
  fullName: 'María García López',
  documentType: 'CC',
  documentNumber: '1061234567',
  phone: '+57 300 123 4567',
};
const CARLOS: PacienteEncontrado = { ...MARIA, patientId: 2, fullName: 'Carlos Rodríguez', documentNumber: '1061234890' };
const LAURA: PacienteEncontrado = { ...MARIA, patientId: 3, fullName: 'Laura Sánchez', documentNumber: '1062345678' };

function cita(id: number, date: string, hora: string, status: Appointment['status']): Appointment {
  return {
    appointmentId: id,
    patientId: 1,
    patientName: 'María García López',
    patientPhone: null,
    doctorId: 1,
    doctorName: 'Dra. Laura Muñoz',
    serviceType: 'CONSULTA_GENERAL',
    date,
    startTime: `${hora}:00`,
    endTime: `${hora}:30`,
    reason: '',
    status,
  };
}

function render() {
  TestBed.configureTestingModule({
    imports: [HistorialPaciente],
    providers: [provideHttpClient(), provideHttpClientTesting()],
  });
  const fixture = TestBed.createComponent(HistorialPaciente);
  fixture.detectChanges();
  return {
    fixture,
    pantalla: fixture.componentInstance,
    http: TestBed.inject(HttpTestingController),
    page: fixture.nativeElement as HTMLElement,
  };
}

function teclear(pantalla: HistorialPaciente, key: string): void {
  pantalla.teclear(new KeyboardEvent('keydown', { key }));
}

describe('HistorialPaciente', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('asks the backend for suggestions from the third digit on', () => {
    const { pantalla, http } = render();

    pantalla.escribir('10');
    vi.advanceTimersByTime(ESPERA_SUGERENCIAS_MS);
    http.expectNone((req) => req.url === BUSQUEDA);

    pantalla.escribir('106123');
    vi.advanceTimersByTime(ESPERA_SUGERENCIAS_MS);
    const request = http.expectOne((req) => req.url === BUSQUEDA);
    expect(request.request.params.get('document')).toBe('106123');
    request.flush([MARIA, CARLOS]);

    expect(pantalla.sugerencias().map((p) => p.fullName)).toEqual(['María García López', 'Carlos Rodríguez']);
  });

  it('says it is searching, not that nobody matches, while the answer is on its way', () => {
    const { fixture, pantalla, http, page } = render();

    pantalla.escribir('1061');
    fixture.detectChanges();
    expect(page.querySelector('.sugerencias')!.textContent).toContain('Buscando pacientes');

    vi.advanceTimersByTime(ESPERA_SUGERENCIAS_MS);
    http.expectOne((req) => req.url === BUSQUEDA).flush([]);
    fixture.detectChanges();
    expect(page.querySelector('.sugerencias')!.textContent).toContain('Ningún paciente');
  });

  it('only asks once the user stops typing', () => {
    const { pantalla, http } = render();

    pantalla.escribir('106');
    pantalla.escribir('1061');
    pantalla.escribir('10612');
    vi.advanceTimersByTime(ESPERA_SUGERENCIAS_MS);

    expect(http.expectOne((req) => req.url === BUSQUEDA).request.params.get('document')).toBe('10612');
  });

  it('picks a suggestion with the keyboard and shows the history from the backend', () => {
    const { fixture, pantalla, http, page } = render();
    pantalla.escribir('106123');
    vi.advanceTimersByTime(ESPERA_SUGERENCIAS_MS);
    http.expectOne((req) => req.url === BUSQUEDA).flush([MARIA, CARLOS]);

    teclear(pantalla, 'ArrowDown');
    teclear(pantalla, 'Enter');
    http
      .expectOne(historialDe(1))
      .flush([
        cita(1, '2026-11-03', '10:30', 'AGENDADA'),
        cita(2, '2026-09-10', '09:00', 'CANCELADA'),
        cita(3, '2026-10-19', '11:30', 'ATENDIDA'),
      ]);
    fixture.detectChanges();

    expect(pantalla.paciente()?.fullName).toBe('María García López');
    expect(pantalla.citas()!.map((c) => c.date)).toEqual(['2026-11-03', '2026-10-19', '2026-09-10']);
    expect(page.querySelectorAll('tbody tr').length).toBe(3);
    expect(page.querySelector('.ficha__total')!.textContent).toContain('3');
  });

  it('finds the exact id number with the Buscar button', () => {
    const { pantalla, http } = render();
    pantalla.escribir('1061234567');

    pantalla.buscar();
    http.expectOne((req) => req.url === BUSQUEDA && req.params.get('document') === '1061234567').flush([MARIA]);

    expect(pantalla.paciente()?.patientId).toBe(1);
    http.expectOne(historialDe(1)).flush([]);
  });

  it('tells the user when no patient has that id number', () => {
    const { fixture, pantalla, http, page } = render();
    pantalla.escribir('999999');

    pantalla.buscar();
    http.expectOne((req) => req.url === BUSQUEDA && req.params.get('document') === '999999').flush([]);
    fixture.detectChanges();

    expect(page.textContent).toContain('Paciente no encontrado');
    expect(page.textContent).toContain('No encontramos un paciente registrado con la cédula 999999');
    expect(page.querySelector('table')).toBeNull();
  });

  it('tells the user when the patient has no appointments yet', () => {
    const { fixture, pantalla, http, page } = render();

    pantalla.elegir(LAURA);
    http.expectOne(historialDe(3)).flush([]);
    fixture.detectChanges();

    expect(page.textContent).toContain('Sin citas registradas');
    expect(page.textContent).toContain('Laura Sánchez no tiene citas registradas');
    expect(page.querySelector('table')).toBeNull();
  });

  it('rejects an id number with dots or letters without calling the backend', () => {
    const { fixture, pantalla, http, page } = render();

    pantalla.escribir('1.061.234');
    vi.advanceTimersByTime(ESPERA_SUGERENCIAS_MS);
    pantalla.buscar();
    fixture.detectChanges();

    http.expectNone((req) => req.url === BUSQUEDA);
    expect(page.querySelector('#cedula')!.classList).toContain('invalid');
    expect(page.textContent).toContain('solo puede tener números');
  });

  it('shows the backend message when the history cannot be loaded', () => {
    const { fixture, pantalla, http, page } = render();

    pantalla.elegir(MARIA);
    http
      .expectOne(historialDe(1))
      .flush({ message: 'No tienes permiso para consultar el historial de citas de un paciente' }, { status: 403, statusText: 'Forbidden' });
    fixture.detectChanges();

    expect(page.querySelector('.alert.error')!.textContent).toContain('No tienes permiso');
  });

  it('highlights the typed digits inside the suggested id number', () => {
    expect(resaltar('1061234567', '106')).toEqual({ coincide: '106', resto: '1234567' });
  });

  it('writes the appointment date short enough to fit in one line', () => {
    expect(fechaCorta('2026-11-03')).toBe('Mar 3 nov 2026');
  });
});
