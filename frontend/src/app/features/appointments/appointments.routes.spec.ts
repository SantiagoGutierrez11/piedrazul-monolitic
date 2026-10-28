import { TestBed } from '@angular/core/testing';
import {
  ActivatedRouteSnapshot,
  CanActivateFn,
  Router,
  RouterStateSnapshot,
  UrlTree,
  provideRouter,
} from '@angular/router';
import { Role } from '../../core/auth/auth.models';
import { AuthService } from '../../core/auth/auth.service';
import { appointmentsRoutes } from './appointments.routes';

// Caso de prueba E7-HU1 4.5: un paciente no puede abrir el historial de otro escribiendo la URL.
function entrarAlHistorialComo(roles: Role[]): boolean | UrlTree {
  TestBed.configureTestingModule({
    providers: [
      provideRouter([]),
      {
        provide: AuthService,
        useValue: {
          isAuthenticated: () => true,
          hasRole: (...allowed: Role[]) => allowed.some((role) => roles.includes(role)),
          homeUrl: () => (roles.includes('paciente') ? '/paciente/inicio' : '/panel/agenda'),
        },
      },
    ],
  });
  const guard = appointmentsRoutes.find((route) => route.path === 'historial')!
    .canActivate![0] as CanActivateFn;
  return TestBed.runInInjectionContext(
    () => guard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot) as boolean | UrlTree,
  );
}

describe('ruta del historial de paciente', () => {
  it.each<Role>(['medico', 'agendador', 'administrador'])('lets the %s in', (rol) => {
    expect(entrarAlHistorialComo([rol])).toBe(true);
  });

  it('sends a patient back to their own home page', () => {
    const resultado = entrarAlHistorialComo(['paciente']);

    expect(TestBed.inject(Router).serializeUrl(resultado as UrlTree)).toBe('/paciente/inicio');
  });
});
