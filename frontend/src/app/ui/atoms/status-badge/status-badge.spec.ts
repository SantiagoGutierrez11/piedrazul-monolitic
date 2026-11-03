import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { StatusBadge } from './status-badge';

@Component({
  imports: [StatusBadge],
  template: `
    <app-status-badge estado="AGENDADA">Agendada</app-status-badge>
    <app-status-badge estado="CANCELADA">Cancelada</app-status-badge>
  `,
})
class Anfitrion {}

describe('StatusBadge', () => {
  it('colors the badge according to the appointment status', () => {
    const fixture = TestBed.createComponent(Anfitrion);
    fixture.detectChanges();
    const [agendada, cancelada] = [
      ...(fixture.nativeElement as HTMLElement).querySelectorAll<HTMLElement>('app-status-badge'),
    ];

    expect(agendada.classList).toContain('badge');
    expect(agendada.classList).toContain('badge--agendada');
    expect(agendada.textContent).toContain('Agendada');
    expect(cancelada.classList).toContain('badge--cancelada');
    expect(cancelada.classList).not.toContain('badge--agendada');
  });
});
