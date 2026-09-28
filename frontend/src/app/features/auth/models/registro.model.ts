export type Genero = 'FEMENINO' | 'MASCULINO' | 'OTRO';
export type TipoDocumento = 'CC' | 'TI' | 'CE' | 'PA';

export const GENEROS: { value: Genero; label: string }[] = [
  { value: 'FEMENINO', label: 'Femenino' },
  { value: 'MASCULINO', label: 'Masculino' },
  { value: 'OTRO', label: 'Otro' },
];

export const TIPOS_DOCUMENTO: { value: TipoDocumento; label: string }[] = [
  { value: 'CC', label: 'Cédula de ciudadanía' },
  { value: 'TI', label: 'Tarjeta de identidad' },
  { value: 'CE', label: 'Cédula de extranjería' },
  { value: 'PA', label: 'Pasaporte' },
];

// Cuerpo de POST /patients/register.
export interface RegistroPaciente {
  firstName: string;
  middleName: string;
  lastName: string;
  secondLastName: string;
  email: string;
  phone: string;
  birthDate: string;
  gender: Genero;
  documentType: TipoDocumento;
  documentNumber: string;
  password: string;
  confirmPassword: string;
}

export interface PacienteRegistrado {
  patientId: number;
  fullName: string;
  email: string;
}
