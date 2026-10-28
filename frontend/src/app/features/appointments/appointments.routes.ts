import { Routes } from '@angular/router';
import { STAFF_ROLES } from '../../core/auth/auth.models';
import { roleGuard } from '../../core/guards/auth-guards';
import { ListarCitas } from './listar-citas/listar-citas';
import { AgendamientoAutonomo } from './agendamiento-autonomo/agendamiento-autonomo';
import { ProximasCitas } from './proximas-citas/proximas-citas';
import { HistorialPaciente } from './historial-paciente/historial-paciente';

// Montado en app.routes.ts bajo /appointments (lazy-loaded).
export const appointmentsRoutes: Routes = [
  { path: 'listar', component: ListarCitas, canActivate: [roleGuard(STAFF_ROLES)] },
  
  { path: 'proximas', component: ProximasCitas, canActivate: [roleGuard(STAFF_ROLES)] },
  // Roles de la HU (médico/terapista y agendador); se confirman en la subtarea 2.3.
  {
    path: 'historial',
    component: HistorialPaciente,
    canActivate: [roleGuard(['medico', 'agendador'])],
  },
  { path: 'agendar', component: AgendamientoAutonomo, canActivate: [roleGuard(['paciente'])] },
];
