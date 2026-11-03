import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { StatCard } from './stat-card';

@Component({
  imports: [StatCard],
  template: `
    <app-stat-card etiqueta="Pacientes hoy" [valor]="12" />
    <app-stat-card etiqueta="Atendidos" valor="8" tono="ok" />
    <app-stat-card etiqueta="Semana con más citas" [valor]="5" tono="warn">
      <span class="detalle">3 al 9 de noviembre</span>
    </app-stat-card>
  `,
})
class Anfitrion {}

describe('StatCard', () => {
  function tarjetas(): HTMLElement[] {
    const fixture = TestBed.createComponent(Anfitrion);
    fixture.detectChanges();
    return [
      ...(fixture.nativeElement as HTMLElement).querySelectorAll<HTMLElement>('app-stat-card'),
    ];
  }

  it('shows the label and the figure inside a card', () => {
    const [pacientes] = tarjetas();

    expect(pacientes.classList).toContain('card');
    expect(pacientes.classList).toContain('stat');
    expect(pacientes.querySelector('small')!.textContent).toBe('Pacientes hoy');
    expect(pacientes.querySelector('strong')!.textContent).toBe('12');
  });

  it('colors the figure according to its tone', () => {
    const [pacientes, atendidos] = tarjetas();

    expect(atendidos.querySelector('strong')!.classList).toContain('ok');
    expect(pacientes.querySelector('strong')!.classList).not.toContain('ok');
  });

  it('shows the projected detail under the figure', () => {
    const [, , semana] = tarjetas();

    expect(semana.querySelector('strong')!.classList).toContain('warn');
    expect(semana.querySelector('.detalle')!.textContent).toBe('3 al 9 de noviembre');
  });
});
