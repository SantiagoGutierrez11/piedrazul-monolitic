import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { API_BASE_URL } from '../../../core/api-config';
import { Registro } from './registro';

const URL = `${API_BASE_URL}/patients/register`;

const DATOS = {
  firstName: 'María',
  middleName: 'Fernanda',
  lastName: 'Gómez',
  secondLastName: 'Rodríguez',
  email: 'maria.gomez@correo.com',
  phone: '300 123 4567',
  birthDate: '1958-04-12',
  gender: 'FEMENINO' as const,
  documentType: 'CC' as const,
  documentNumber: '1023456789',
  password: 'clave1234',
  confirmPassword: 'clave1234',
};

describe('Registro', () => {
  let fixture: ComponentFixture<Registro>;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [Registro],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    fixture = TestBed.createComponent(Registro);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  function element(): HTMLElement {
    return fixture.nativeElement as HTMLElement;
  }

  function enviar(datos = DATOS): void {
    fixture.componentInstance.form.setValue(datos);
    fixture.componentInstance.crearCuenta();
  }

  it('does not send the form when the passwords do not match', () => {
    enviar({ ...DATOS, confirmPassword: 'otra-clave' });
    fixture.detectChanges();

    expect(element().textContent).toContain('Las contraseñas no coinciden');
    http.expectNone(URL);
  });

  it('flags the required fields of an empty form', () => {
    fixture.componentInstance.crearCuenta();
    fixture.detectChanges();

    expect(element().textContent).toContain('El primer nombre es obligatorio');
    expect(element().textContent).toContain('Selecciona el tipo de documento');
    http.expectNone(URL);
  });

  it('shows the confirmation after creating the account', () => {
    enviar();
    const request = http.expectOne(URL);
    request.flush(
      { patientId: 10, fullName: 'María Fernanda Gómez Rodríguez', email: DATOS.email },
      { status: 201, statusText: 'Created' },
    );
    fixture.detectChanges();

    expect(request.request.body.documentNumber).toBe('1023456789');
    expect(element().querySelector('[role="dialog"] h2')?.textContent).toContain(
      '¡Cuenta Creada Exitosamente!',
    );
  });

  it('shows the conflict reported by the server', () => {
    enviar();
    http
      .expectOne(URL)
      .flush(
        { message: 'Ya existe un paciente registrado con ese documento' },
        { status: 409, statusText: 'Conflict' },
      );
    fixture.detectChanges();

    expect(element().querySelector('[role="alert"]')?.textContent).toContain(
      'Ya existe un paciente registrado con ese documento',
    );
    expect(element().querySelector('[role="dialog"]')).toBeNull();
  });
});
