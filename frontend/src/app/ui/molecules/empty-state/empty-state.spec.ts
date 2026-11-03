import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { EmptyState } from './empty-state';

@Component({
  imports: [EmptyState],
  template: `
    <app-empty-state>Cargando tu agenda...</app-empty-state>
    <app-empty-state tarjeta>No hay citas para los filtros seleccionados.</app-empty-state>
  `,
})
class Anfitrion {}

describe('EmptyState', () => {
  function mensajes(): HTMLElement[] {
    const fixture = TestBed.createComponent(Anfitrion);
    fixture.detectChanges();
    return [
      ...(fixture.nativeElement as HTMLElement).querySelectorAll<HTMLElement>('app-empty-state'),
    ];
  }

  it('shows the message inside a block that is already a card', () => {
    const [bloque] = mensajes();

    expect(bloque.textContent).toContain('Cargando tu agenda');
    expect(bloque.classList).toContain('vacio');
    expect(bloque.classList).not.toContain('card');
  });

  it('can take its own card', () => {
    const [, tarjeta] = mensajes();

    expect(tarjeta.classList).toContain('card');
    expect(tarjeta.classList).toContain('empty-state');
    expect(tarjeta.classList).not.toContain('vacio');
  });
});
