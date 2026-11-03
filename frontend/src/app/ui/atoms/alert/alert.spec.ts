import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { Alert } from './alert';

@Component({
  imports: [Alert],
  template: `
    <app-alert tono="error">Falló</app-alert>
    <app-alert tono="ok">Listo</app-alert>
    <app-alert tono="aviso">Ojo</app-alert>
    <app-alert>Dato</app-alert>
  `,
})
class Anfitrion {}

describe('Alert', () => {
  function alertas(): HTMLElement[] {
    const fixture = TestBed.createComponent(Anfitrion);
    fixture.detectChanges();
    return [...(fixture.nativeElement as HTMLElement).querySelectorAll<HTMLElement>('app-alert')];
  }

  it('shows an error as an alert for screen readers', () => {
    const [error] = alertas();

    expect(error.classList).toContain('alert');
    expect(error.classList).toContain('error');
    expect(error.getAttribute('role')).toBe('alert');
    expect(error.textContent).toContain('Falló');
  });

  it('announces a success without interrupting', () => {
    const [, ok] = alertas();

    expect(ok.classList).toContain('ok');
    expect(ok.getAttribute('role')).toBe('status');
  });

  it('uses the warning and info tones without a role', () => {
    const [, , aviso, info] = alertas();

    expect(aviso.classList).toContain('aviso');
    expect(aviso.getAttribute('role')).toBeNull();
    expect(info.classList).toContain('info');
    expect(info.getAttribute('role')).toBeNull();
  });
});
