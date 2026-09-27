import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { API_BASE_URL } from '../api-config';
import { SessionResponse } from '../auth/auth.models';
import { AuthService } from '../auth/auth.service';
import { authInterceptor } from './auth-interceptor';

const DOCTORS = `${API_BASE_URL}/medical/doctors`;

function session(accessToken: string, expiresIn: number): SessionResponse {
  return {
    accessToken,
    refreshToken: 'renovacion',
    expiresIn,
    refreshExpiresIn: 7200,
    user: { id: 'u1', email: 'agendador@piedrazul.com', fullName: 'Agendador', roles: ['agendador'] },
  };
}

describe('authInterceptor', () => {
  let client: HttpClient;
  let auth: AuthService;
  let http: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
        // Al vencer la sesión se navega al inicio de sesión.
        provideRouter([{ path: 'login', children: [] }]),
      ],
    });
    client = TestBed.inject(HttpClient);
    auth = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  });

  function loginWith(expiresIn: number): void {
    auth.login('agendador@piedrazul.com', 'agendador123', false).subscribe();
    http.expectOne(`${API_BASE_URL}/auth/login`).flush(session('acceso', expiresIn));
  }

  it('sends the access token to the API', () => {
    loginWith(1800);

    client.get(DOCTORS).subscribe();

    expect(http.expectOne(DOCTORS).request.headers.get('Authorization')).toBe('Bearer acceso');
  });

  it('does not send a token to patient registration', () => {
    loginWith(1800);

    client.post(`${API_BASE_URL}/patients/register`, {}).subscribe();

    const request = http.expectOne(`${API_BASE_URL}/patients/register`);
    expect(request.request.headers.has('Authorization')).toBe(false);
  });

  it('renews an expired token before calling the API', () => {
    loginWith(0);

    client.get(DOCTORS).subscribe();
    http.expectOne(`${API_BASE_URL}/auth/refresh`).flush(session('acceso-renovado', 1800));

    const request = http.expectOne(DOCTORS);
    expect(request.request.headers.get('Authorization')).toBe('Bearer acceso-renovado');
  });

  it('ends the session when the API rejects the token', () => {
    loginWith(1800);

    client.get(DOCTORS).subscribe({ error: () => undefined });
    http
      .expectOne(DOCTORS)
      .flush({ message: 'Token inválido' }, { status: 401, statusText: 'Unauthorized' });

    expect(auth.isAuthenticated()).toBe(false);
  });
});
