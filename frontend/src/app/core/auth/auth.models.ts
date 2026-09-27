// Roles del realm "piedrazul" en Keycloak (ver keycloak/realm-piedrazul.json).
export type Role = 'paciente' | 'agendador' | 'medico' | 'administrador';

export const STAFF_ROLES: Role[] = ['agendador', 'medico', 'administrador'];

export const ROLE_LABELS: Record<Role, string> = {
  paciente: 'Paciente',
  agendador: 'Agendador',
  medico: 'Médico',
  administrador: 'Administrador',
};

export interface AuthUser {
  id: string;
  email: string;
  fullName: string;
  roles: Role[];
}

export interface SessionResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  refreshExpiresIn: number;
  user: AuthUser;
}

export interface StoredSession {
  accessToken: string;
  refreshToken: string;
  // Instante (ms) en que vence el token de acceso.
  expiresAt: number;
  // true: sobrevive al cierre del navegador (localStorage); false: solo la pestaña actual.
  remember: boolean;
  user: AuthUser;
}
