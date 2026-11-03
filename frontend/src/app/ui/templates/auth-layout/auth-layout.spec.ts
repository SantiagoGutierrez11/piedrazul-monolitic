import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { AuthLayout } from './auth-layout';

@Component({
  imports: [AuthLayout],
  template: `
    <app-auth-layout subtitulo="Citas Médicas"
      ><section class="tarjeta">Formulario</section></app-auth-layout
    >
    <app-auth-layout compacto titulo="Crear cuenta" subtitulo="Regístrate para agendar tus citas" />
  `,
})
class Anfitrion {}

describe('AuthLayout', () => {
  function plantillas(): HTMLElement[] {
    const fixture = TestBed.createComponent(Anfitrion);
    fixture.detectChanges();
    return [
      ...(fixture.nativeElement as HTMLElement).querySelectorAll<HTMLElement>('app-auth-layout'),
    ];
  }

  it('shows the clinic brand above the projected form', () => {
    const [inicio] = plantillas();

    expect(inicio.querySelector('.brand-mark')).not.toBeNull();
    expect(inicio.querySelector('.auth-brand strong')!.textContent).toBe('Piedrazul');
    expect(inicio.querySelector('.auth-brand small')!.textContent).toBe('Citas Médicas');
    expect(inicio.querySelector('.auth-page > .tarjeta')!.textContent).toBe('Formulario');
  });

  it('shows the screen title instead of the clinic name in the compact version', () => {
    const [, registro] = plantillas();

    expect(registro.querySelector('.auth-brand')!.classList).toContain('compact');
    expect(registro.querySelector('.auth-brand h1')!.textContent).toBe('Crear cuenta');
    expect(registro.querySelector('.auth-brand strong')).toBeNull();
  });
});
