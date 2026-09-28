import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Role } from '../auth/auth.models';
import { AuthService } from '../auth/auth.service';

/** Solo usuarios con sesión iniciada. */
export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.isAuthenticated() || inject(Router).createUrlTree(['/login']);
};

/** Inicio de sesión y registro: si ya hay sesión se envía al usuario a su pantalla inicial. */
export const guestGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return !auth.isAuthenticated() || inject(Router).parseUrl(auth.homeUrl());
};

/**
 * Exige al menos uno de los roles indicados.
 * Uso: { path: 'configuration', canActivate: [roleGuard(['administrador'])], ... }
 */
export const roleGuard = (allowedRoles: Role[]): CanActivateFn => {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);
    if (!auth.isAuthenticated()) {
      return router.createUrlTree(['/login']);
    }
    return auth.hasRole(...allowedRoles) || router.parseUrl(auth.homeUrl());
  };
};
