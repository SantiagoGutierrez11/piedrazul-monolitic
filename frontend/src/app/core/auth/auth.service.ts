import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, finalize, map, shareReplay, tap } from 'rxjs';
import { API_BASE_URL } from '../api-config';
import { AuthUser, Role, SessionResponse, StoredSession } from './auth.models';

const STORAGE_KEY = 'piedrazul_session';
// Se renueva el token un poco antes de que venza para no enviar uno expirado.
const EXPIRY_MARGIN_MS = 30_000;

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly baseUrl = `${API_BASE_URL}/auth`;

  private readonly session = signal<StoredSession | null>(readStoredSession());
  private refreshInFlight: Observable<StoredSession> | null = null;

  readonly user = computed(() => this.session()?.user ?? null);
  readonly isAuthenticated = computed(() => this.session() !== null);

  login(email: string, password: string, remember: boolean): Observable<AuthUser> {
    return this.http
      .post<SessionResponse>(`${this.baseUrl}/login`, { email, password })
      .pipe(map((response) => this.store(response, remember).user));
  }

  /** Cierra la sesión en Keycloak (sin esperar respuesta) y limpia la sesión local. */
  logout(options: { redirect: boolean } = { redirect: true }): void {
    const current = this.session();
    if (current) {
      this.http
        .post(`${this.baseUrl}/logout`, { refreshToken: current.refreshToken })
        .subscribe({ error: () => undefined });
    }
    this.clear();
    if (options.redirect) {
      this.router.navigate(['/login']);
    }
  }

  /** La sesión ya no es válida en el servidor: se descarta y se vuelve al inicio de sesión. */
  expireSession(): void {
    if (this.session()) {
      this.clear();
      this.router.navigate(['/login'], { state: { sessionExpired: true } });
    }
  }

  accessToken(): string | null {
    return this.session()?.accessToken ?? null;
  }

  isAccessTokenExpired(): boolean {
    const current = this.session();
    return !!current && Date.now() >= current.expiresAt - EXPIRY_MARGIN_MS;
  }

  /** Renueva el token; si varias peticiones lo piden a la vez, comparten la misma renovación. */
  refresh(): Observable<StoredSession> {
    const current = this.session();
    if (!current) {
      throw new Error('No hay una sesión que renovar');
    }
    this.refreshInFlight ??= this.http
      .post<SessionResponse>(`${this.baseUrl}/refresh`, { refreshToken: current.refreshToken })
      .pipe(
        map((response) => this.store(response, current.remember)),
        finalize(() => (this.refreshInFlight = null)),
        shareReplay(1),
      );
    return this.refreshInFlight;
  }

  hasRole(...roles: Role[]): boolean {
    const userRoles = this.user()?.roles ?? [];
    return roles.some((role) => userRoles.includes(role));
  }

  /** Pantalla inicial según el rol del usuario. */
  homeUrl(): string {
    if (this.hasRole('administrador')) {
      return '/panel/admin';
    }
    if (this.hasRole('agendador')) {
      return '/panel/agenda';
    }
    if (this.hasRole('medico')) {
      return '/panel/medico';
    }
    if (this.hasRole('paciente')) {
      return '/paciente/inicio';
    }
    return '/login';
  }

  private store(response: SessionResponse, remember: boolean): StoredSession {
    const session: StoredSession = {
      accessToken: response.accessToken,
      refreshToken: response.refreshToken,
      expiresAt: Date.now() + response.expiresIn * 1000,
      remember,
      user: response.user,
    };
    removeStoredSession();
    (remember ? localStorage : sessionStorage).setItem(STORAGE_KEY, JSON.stringify(session));
    this.session.set(session);
    return session;
  }

  private clear(): void {
    removeStoredSession();
    this.session.set(null);
  }
}

function readStoredSession(): StoredSession | null {
  const raw = localStorage.getItem(STORAGE_KEY) ?? sessionStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as StoredSession;
  } catch {
    removeStoredSession();
    return null;
  }
}

function removeStoredSession(): void {
  localStorage.removeItem(STORAGE_KEY);
  sessionStorage.removeItem(STORAGE_KEY);
}
