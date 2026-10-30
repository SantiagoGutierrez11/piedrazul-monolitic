import { Appointment } from '../models/appointment.model';
import {
  ERRORES_CEDULA,
  errorDeFormato,
  errorParaBuscar,
  masRecientePrimero,
  sugerirDesde,
} from './historial-paciente.reglas';

describe('reglas de la búsqueda por cédula (2.1)', () => {
  it('accepts only digits, up to ten', () => {
    expect(errorDeFormato('1061234567')).toBeNull();
    expect(errorDeFormato('1.061.234.567')).toBe(ERRORES_CEDULA.formato);
    expect(errorDeFormato('10612a')).toBe(ERRORES_CEDULA.formato);
    expect(errorDeFormato('106 123')).toBe(ERRORES_CEDULA.formato);
    expect(errorDeFormato('10612345678')).toBe(ERRORES_CEDULA.larga);
  });

  it('suggests patients from the third digit on', () => {
    expect(sugerirDesde('10')).toBe(false);
    expect(sugerirDesde('106')).toBe(true);
    expect(sugerirDesde('10a')).toBe(false);
  });

  it('needs at least five digits to search an exact id number', () => {
    expect(errorParaBuscar('1061')).toBe(ERRORES_CEDULA.corta);
    expect(errorParaBuscar('94512345')).toBeNull();
  });
});

describe('orden del historial (2.2)', () => {
  it('puts the newest appointment first, and the later time first on the same day', () => {
    const cita = (date: string, startTime: string) => ({ date, startTime }) as Appointment;

    const ordenadas = masRecientePrimero([
      cita('2026-09-10', '09:00:00'),
      cita('2026-11-03', '10:00:00'),
      cita('2026-09-10', '11:00:00'),
    ]);

    expect(ordenadas.map((c) => `${c.date} ${c.startTime}`)).toEqual([
      '2026-11-03 10:00:00',
      '2026-09-10 11:00:00',
      '2026-09-10 09:00:00',
    ]);
  });
});
