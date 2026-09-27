import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { API_BASE_URL } from '../../../core/api-config';
import { AuthService } from '../../../core/auth/auth.service';
import { Login } from './login';

describe('Login', () => {
  let fixture: ComponentFixture<Login>;
  let http: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    TestBed.configureTestingModule({
      imports: [Login],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    fixture = TestBed.createComponent(Login);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  function text(): string {
    return (fixture.nativeElement as HTMLElement).textContent!;
  }

  it('shows the required-field errors when submitting an empty form', () => {
    fixture.componentInstance.ingresar();
    fixture.detectChanges();

    expect(text()).toContain('El correo electrónico es obligatorio');
    expect(text()).toContain('La contraseña es obligatoria');
    http.expectNone(`${API_BASE_URL}/auth/login`);
  });

  it('rejects a staff account signing in from the patient tab', () => {
    const login = fixture.componentInstance;
    login.form.setValue({ email: 'admin@piedrazul.com', password: 'admin123', recordarme: false });

    login.ingresar();
    http.expectOne(`${API_BASE_URL}/auth/login`).flush({
      accessToken: 'acceso',
      refreshToken: 'renovacion',
      expiresIn: 1800,
      refreshExpiresIn: 7200,
      user: { id: 'u1', email: 'admin@piedrazul.com', fullName: 'Admin Sistema', roles: ['administrador'] },
    });
    http.expectOne(`${API_BASE_URL}/auth/logout`).flush(null);
    fixture.detectChanges();

    expect(text()).toContain('Esta cuenta es de un profesional');
    expect(TestBed.inject(AuthService).isAuthenticated()).toBe(false);
  });

  it('shows the message returned by the server for wrong credentials', () => {
    const login = fixture.componentInstance;
    login.form.setValue({ email: 'admin@piedrazul.com', password: 'mala', recordarme: false });

    login.ingresar();
    http
      .expectOne(`${API_BASE_URL}/auth/login`)
      .flush({ message: 'Correo o contraseña incorrectos' }, { status: 401, statusText: 'Unauthorized' });
    fixture.detectChanges();

    expect(text()).toContain('Correo o contraseña incorrectos');
  });
});
