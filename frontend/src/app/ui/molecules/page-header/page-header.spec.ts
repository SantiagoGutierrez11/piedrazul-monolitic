import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { PageHeader } from './page-header';

@Component({
  imports: [PageHeader],
  template: `
    <app-page-header titulo="Resumen General" subtitulo="Lunes 2 de noviembre">
      <a class="boton">Ver próximas citas</a>
    </app-page-header>
    <app-page-header
      ruta="Administración / Listado"
      titulo="Listado de Citas"
      subtitulo="Filtra las citas."
    />
    <app-page-header grande titulo="Hola, María" />
  `,
})
class Anfitrion {}

describe('PageHeader', () => {
  function encabezados(): HTMLElement[] {
    const fixture = TestBed.createComponent(Anfitrion);
    fixture.detectChanges();
    return [
      ...(fixture.nativeElement as HTMLElement).querySelectorAll<HTMLElement>('app-page-header'),
    ];
  }

  it('shows the title, the subtitle and the actions of a panel', () => {
    const [panel] = encabezados();

    expect(panel.querySelector('h1')!.textContent).toBe('Resumen General');
    expect(panel.querySelector('.subtitle')!.textContent).toBe('Lunes 2 de noviembre');
    expect(panel.querySelector('.acciones .boton')!.textContent).toContain('Ver próximas citas');
  });

  it('shows the breadcrumb above the title when a route is given', () => {
    const [, pantalla] = encabezados();

    expect(pantalla.querySelector('.breadcrumb')!.textContent).toBe('Administración / Listado');
    expect(pantalla.querySelector('h1')!.textContent).toBe('Listado de Citas');
    expect(pantalla.querySelector('.panel-header')).toBeNull();
  });

  it('omits the subtitle when there is none and enlarges the greeting', () => {
    const [, , inicio] = encabezados();

    expect(inicio.querySelector('.subtitle')).toBeNull();
    expect(inicio.classList).toContain('grande');
  });
});
