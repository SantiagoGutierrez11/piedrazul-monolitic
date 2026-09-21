import { CanActivateFn } from '@angular/router';

// TODO: reemplazar por el rol real del usuario autenticado (ver AuthContext.jsx original).
// Uso: { path: 'admin/configuration', canActivate: [roleGuard(['ADMIN'])], ... }
export const roleGuard = (allowedRoles: string[]): CanActivateFn => {
  return () => {
    const userRole = localStorage.getItem('piedrazul_role');
    return !!userRole && allowedRoles.includes(userRole);
  };
};
