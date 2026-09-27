import { HttpErrorResponse, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, map, of, switchMap, throwError } from 'rxjs';
import { API_BASE_URL } from '../api-config';
import { AuthService } from '../auth/auth.service';

// Endpoints que no llevan token: se usan justamente para obtenerlo o antes de tener cuenta.
const PUBLIC_PATHS = ['/auth/login', '/auth/refresh', '/auth/logout', '/patients/register'];

// Adjunta el token de acceso a cada petición al backend y lo renueva cuando está por vencer.
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);

  if (!req.url.startsWith(API_BASE_URL) || isPublic(req) || !auth.isAuthenticated()) {
    return next(req);
  }

  const token$ = auth.isAccessTokenExpired()
    ? auth.refresh().pipe(map((session) => session.accessToken))
    : of(auth.accessToken()!);

  return token$.pipe(
    switchMap((token) => next(req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }))),
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse && error.status === 401) {
        auth.expireSession();
      }
      return throwError(() => error);
    }),
  );
};

function isPublic(req: HttpRequest<unknown>): boolean {
  const path = req.url.slice(API_BASE_URL.length);
  return PUBLIC_PATHS.includes(path);
}
