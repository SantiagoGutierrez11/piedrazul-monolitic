import { DatosRegistro, formularioValido, validarCampo } from './registro.validaciones';

const DATOS: DatosRegistro = {
  firstName: 'María',
  middleName: '',
  lastName: 'García',
  secondLastName: 'López',
  email: 'maria@correo.com',
  phone: '300 123 4567',
  birthDate: '1990-05-10',
  gender: 'FEMENINO',
  documentType: 'CC',
  documentNumber: '1061234567',
  password: 'segura123',
  confirmPassword: 'segura123',
};

describe('validaciones del registro', () => {
  it('acepta un formulario completo y correcto', () => {
    expect(formularioValido(DATOS)).toBe(true);
  });

  it('explica qué está mal en cada campo', () => {
    const datos = {
      ...DATOS,
      firstName: 'M4ría',
      phone: '12',
      birthDate: '2999-01-01',
      documentNumber: '12.345',
    };

    expect(validarCampo('firstName', datos)).toBe('Usa solo letras (mínimo 2)');
    expect(validarCampo('phone', datos)).toContain('entre 7 y 15 dígitos');
    expect(validarCampo('birthDate', datos)).toBe('La fecha no puede ser posterior a hoy');
    expect(validarCampo('documentNumber', datos)).toContain('sin puntos ni espacios');
    expect(formularioValido(datos)).toBe(false);
  });

  it('pide los campos obligatorios y compara las contraseñas', () => {
    const datos = { ...DATOS, email: '', password: 'corta', confirmPassword: 'otra' };

    expect(validarCampo('email', datos)).toBe('El correo electrónico es obligatorio');
    expect(validarCampo('password', datos)).toBe('La contraseña debe tener mínimo 8 caracteres');
    expect(validarCampo('confirmPassword', datos)).toBe('Las contraseñas no coinciden');
    expect(validarCampo('middleName', datos)).toBe('');
  });
});
