import { TestBed } from '@angular/core/testing';
import { HistorialPaciente, fechaCorta, resaltar } from './historial-paciente';

function render() {
  TestBed.configureTestingModule({ imports: [HistorialPaciente] });
  const fixture = TestBed.createComponent(HistorialPaciente);
  fixture.detectChanges();
  return { fixture, pantalla: fixture.componentInstance, page: fixture.nativeElement as HTMLElement };
}

function teclear(pantalla: HistorialPaciente, key: string): void {
  pantalla.teclear(new KeyboardEvent('keydown', { key }));
}

describe('HistorialPaciente (diseño con datos de muestra)', () => {
  it('suggests patients only from the third digit on', () => {
    const { pantalla } = render();

    pantalla.escribir('10');
    expect(pantalla.sugerencias()).toEqual([]);

    pantalla.escribir('106123');
    expect(pantalla.sugerencias().map((p) => p.fullName)).toEqual([
      'María García López',
      'Carlos Rodríguez',
    ]);
  });

  it('picks a suggestion with the keyboard and shows the newest appointment first', () => {
    const { fixture, pantalla, page } = render();

    pantalla.escribir('106123');
    teclear(pantalla, 'ArrowDown');
    teclear(pantalla, 'Enter');
    fixture.detectChanges();

    expect(pantalla.paciente()?.fullName).toBe('María García López');
    expect(pantalla.citas().map((c) => c.date)).toEqual([
      '2026-11-03',
      '2026-10-19',
      '2026-09-24',
      '2026-09-10',
      '2026-08-21',
    ]);
    expect(page.querySelectorAll('tbody tr').length).toBe(5);
  });

  it('tells the user when no patient has that id number', () => {
    const { fixture, pantalla, page } = render();

    pantalla.escribir('999999');
    pantalla.buscar();
    fixture.detectChanges();

    expect(page.textContent).toContain('Paciente no encontrado');
    expect(page.textContent).toContain('No encontramos un paciente registrado con la cédula 999999');
  });

  it('tells the user when the patient has no appointments yet', () => {
    const { fixture, pantalla, page } = render();

    pantalla.escribir('1062345678');
    pantalla.buscar();
    fixture.detectChanges();

    expect(page.textContent).toContain('Sin citas registradas');
    expect(page.querySelector('table')).toBeNull();
  });

  it('highlights the typed digits inside the suggested id number', () => {
    expect(resaltar('1061234567', '106')).toEqual({ coincide: '106', resto: '1234567' });
  });

  it('writes the appointment date short enough to fit in one line', () => {
    expect(fechaCorta('2026-11-03')).toBe('Mar 3 nov 2026');
  });
});
