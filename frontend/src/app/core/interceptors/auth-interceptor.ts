import { HttpInterceptorFn } from '@angular/common/http';

// Adjunta el JWT a cada request al backend (por ahora desde localStorage; con Keycloak más adelante).
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('piedrazul_token');
  if (!token) {
    return next(req);
  }
  return next(
    req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    })
  );
};
