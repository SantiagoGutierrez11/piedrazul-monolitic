import { aIso, fechaCompleta, fechaLarga, horaAmPm } from './fechas';

describe('fechas', () => {
  it('writes dates the way patients read them', () => {
    expect(fechaLarga('2026-10-13')).toBe('Martes 13 de octubre');
    expect(fechaCompleta('2026-09-27')).toBe('Domingo 27 de septiembre de 2026');
  });

  it('uses a 12-hour clock with a. m. and p. m.', () => {
    expect(horaAmPm('09:00:00')).toBe('9:00 a. m.');
    expect(horaAmPm('12:00')).toBe('12:00 p. m.');
    expect(horaAmPm('14:30')).toBe('2:30 p. m.');
    expect(horaAmPm('00:15')).toBe('12:15 a. m.');
  });

  it('keeps the local calendar day', () => {
    expect(aIso(new Date(2026, 2, 9))).toBe('2026-03-09');
  });
});
