// Reglas del formulario de registro. Cada función recibe el valor escrito y devuelve el
// mensaje de error, o '' si el valor es correcto.

export interface DatosRegistro {
  firstName: string;
  middleName: string;
  lastName: string;
  secondLastName: string;
  email: string;
  phone: string;
  birthDate: string;
  gender: string;
  documentType: string;
  documentNumber: string;
  password: string;
  confirmPassword: string;
}

export type Campo = keyof DatosRegistro;

const SOLO_LETRAS = /^[A-Za-zÀ-ÿ' -]*$/;
const CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const TELEFONO = /^\+?\d{7,15}$/;
const DOCUMENTO = /^[A-Za-z0-9]{5,15}$/;

function nombreObligatorio(valor: string, mensajeVacio: string): string {
  const texto = valor.trim();
  if (!texto) return mensajeVacio;
  if (texto.length < 2 || !SOLO_LETRAS.test(texto)) return 'Usa solo letras (mínimo 2)';
  return '';
}

function nombreOpcional(valor: string): string {
  return SOLO_LETRAS.test(valor.trim()) ? '' : 'Usa solo letras';
}

function correo(valor: string): string {
  const texto = valor.trim();
  if (!texto) return 'El correo electrónico es obligatorio';
  if (!CORREO.test(texto)) return 'Ingresa un correo válido, por ejemplo nombre@correo.com';
  return '';
}

function telefono(valor: string): string {
  const digitos = valor.replace(/[\s-]/g, '');
  if (!digitos) return 'El teléfono es obligatorio';
  if (!TELEFONO.test(digitos)) return 'Ingresa entre 7 y 15 dígitos, por ejemplo 300 123 4567';
  return '';
}

function fechaNacimiento(valor: string): string {
  if (!valor) return 'La fecha de nacimiento es obligatoria';
  if (valor > hoyLocal()) return 'La fecha no puede ser posterior a hoy';
  return '';
}

function documento(valor: string): string {
  const texto = valor.trim();
  if (!texto) return 'El número de documento es obligatorio';
  if (!DOCUMENTO.test(texto)) return 'Usa entre 5 y 15 números o letras, sin puntos ni espacios';
  return '';
}

function contrasena(valor: string): string {
  if (!valor) return 'La contraseña es obligatoria';
  if (valor.length < 8) return 'La contraseña debe tener mínimo 8 caracteres';
  return '';
}

function confirmacion(valor: string, contrasenaEscrita: string): string {
  if (!valor) return 'Confirma tu contraseña';
  if (valor !== contrasenaEscrita) return 'Las contraseñas no coinciden';
  return '';
}

/** Mensaje de error de un campo, o '' si está bien. */
export function validarCampo(campo: Campo, datos: DatosRegistro): string {
  const valor = datos[campo];
  switch (campo) {
    case 'firstName':
      return nombreObligatorio(valor, 'El primer nombre es obligatorio');
    case 'lastName':
      return nombreObligatorio(valor, 'El primer apellido es obligatorio');
    case 'middleName':
    case 'secondLastName':
      return nombreOpcional(valor);
    case 'email':
      return correo(valor);
    case 'phone':
      return telefono(valor);
    case 'birthDate':
      return fechaNacimiento(valor);
    case 'gender':
      return valor ? '' : 'Selecciona un género';
    case 'documentType':
      return valor ? '' : 'Selecciona el tipo de documento';
    case 'documentNumber':
      return documento(valor);
    case 'password':
      return contrasena(valor);
    case 'confirmPassword':
      return confirmacion(valor, datos.password);
  }
}

/** true si todos los campos del formulario son válidos. */
export function formularioValido(datos: DatosRegistro): boolean {
  return (Object.keys(datos) as Campo[]).every((campo) => validarCampo(campo, datos) === '');
}

/** Fecha de hoy (AAAA-MM-DD) en la zona horaria del usuario, como la muestra el calendario. */
export function hoyLocal(): string {
  const ahora = new Date();
  return new Date(ahora.getTime() - ahora.getTimezoneOffset() * 60_000).toISOString().slice(0, 10);
}
