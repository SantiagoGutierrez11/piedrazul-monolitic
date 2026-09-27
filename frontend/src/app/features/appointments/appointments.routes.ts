import { Routes } from '@angular/router';
import { STAFF_ROLES } from '../../core/auth/auth.models';
import { roleGuard } from '../../core/guards/auth-guards';
import { ListarCitas } from './listar-citas/listar-citas';
import { AgendamientoAutonomo } from './agendamiento-autonomo/agendamiento-autonomo';

// Montado en app.routes.ts bajo /appointments (lazy-loaded).
export const appointmentsRoutes: Routes = [
  { path: 'listar', component: ListarCitas, canActivate: [roleGuard(STAFF_ROLES)] },
  {
    path: 'agendar',
    component: AgendamientoAutonomo,
    canActivate: [roleGuard(['paciente', 'agendador'])],
  },
];
