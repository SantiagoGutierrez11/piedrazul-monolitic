import { HttpErrorResponse } from '@angular/common/http';

/** Mensaje para el usuario a partir de una respuesta de error del backend. */
export function mensajeDeError(response: HttpErrorResponse, porDefecto: string): string {
  if (response.status === 0) {
    return 'No fue posible conectar con el servidor. Verifica tu conexión e intenta de nuevo.';
  }
  const mensaje = response.error?.message;
  return typeof mensaje === 'string' && mensaje ? mensaje : porDefecto;
}
