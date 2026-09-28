import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { API_BASE_URL } from '../api-config';
import { Role, SessionResponse } from './auth.models';
import { AuthService } from './auth.service';

const KEY = 'piedrazul_session';

function sessionFor(roles: Role[]): SessionResponse {
  return {
    accessToken: 'acceso',
    refreshToken: 'renovacion',
    expiresIn: 1800,
    refreshExpiresIn: 7200,
    user: { id: 'u1', email: 'usuario@piedrazul.com', fullName: 'Usuario Prueba', roles },
  };
}

describe('AuthService', () => {
  let auth: AuthService;
  let http: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    auth = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  });

  function login(roles: Role[], remember = false): void {
    auth.login('usuario@piedrazul.com', 'clave1234', remember).subscribe();
    http.expectOne(`${API_BASE_URL}/auth/login`).flush(sessionFor(roles));
  }

  it('keeps the session in localStorage when "Recordarme" is checked', () => {
    login(['administrador'], true);

    expect(localStorage.getItem(KEY)).not.toBeNull();
    expect(sessionStorage.getItem(KEY)).toBeNull();
    expect(auth.isAuthenticated()).toBe(true);
  });

  it('keeps the session only for the current tab otherwise', () => {
    login(['paciente']);

    expect(sessionStorage.getItem(KEY)).not.toBeNull();
    expect(localStorage.getItem(KEY)).toBeNull();
  });

  it('sends each role to its home screen', () => {
    const homes: [Role, string][] = [
      ['administrador', '/configuration'],
      ['agendador', '/appointments/listar'],
      ['medico', '/appointments/listar'],
      ['paciente', '/paciente/inicio'],
    ];
    for (const [role, home] of homes) {
      login([role]);
      expect(auth.homeUrl()).toBe(home);
    }
  });

  it('clears the session on logout', () => {
    login(['agendador'], true);

    auth.logout({ redirect: false });
    http.expectOne(`${API_BASE_URL}/auth/logout`).flush(null);

    expect(auth.isAuthenticated()).toBe(false);
    expect(localStorage.getItem(KEY)).toBeNull();
  });
});
