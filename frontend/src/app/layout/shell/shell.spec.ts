import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AuthUser, Role } from '../../core/auth/auth.models';
import { AuthService } from '../../core/auth/auth.service';
import { Shell } from './shell';

function renderFor(roles: Role[], fullName = 'Admin Sistema'): HTMLElement {
  const user = signal<AuthUser | null>({ id: '1', email: 'x@piedrazul.com', fullName, roles });
  TestBed.configureTestingModule({
    imports: [Shell],
    providers: [
      provideRouter([]),
      {
        provide: AuthService,
        useValue: {
          user,
          hasRole: (...allowed: Role[]) => allowed.some((role) => roles.includes(role)),
          logout: () => undefined,
        },
      },
    ],
  });
  const fixture = TestBed.createComponent(Shell);
  fixture.detectChanges();
  return fixture.nativeElement as HTMLElement;
}

describe('Shell', () => {
  it('shows the administration options to an administrator', () => {
    const nav = renderFor(['administrador']).querySelector('nav')!.textContent!;

    expect(nav).toContain('Listar Citas');
    expect(nav).toContain('Configuración');
    expect(nav).not.toContain('Agendar Cita');
  });

  it('shows only the patient options to a patient', () => {
    const nav = renderFor(['paciente'], 'María García').querySelector('nav')!.textContent!;

    expect(nav).toContain('Inicio');
    expect(nav).toContain('Agendar Cita');
    expect(nav).toContain('Mis Citas');
    expect(nav).not.toContain('Listar Citas');
    expect(nav).not.toContain('Configuración');
  });

  it('shows the signed-in user and role', () => {
    const card = renderFor(['medico'], 'Laura Muñoz').querySelector('.user-info')!.textContent!;

    expect(card).toContain('Laura Muñoz');
    expect(card).toContain('Médico');
  });
});
