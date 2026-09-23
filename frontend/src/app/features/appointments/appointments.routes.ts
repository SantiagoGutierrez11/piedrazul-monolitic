import { Routes } from '@angular/router';
import { ListarCitas } from './listar-citas/listar-citas';
import { AgendamientoAutonomo } from './agendamiento-autonomo/agendamiento-autonomo';

// Montado en app.routes.ts bajo /appointments (lazy-loaded).
export const appointmentsRoutes: Routes = [
  { path: 'listar', component: ListarCitas }, // Andrea
  { path: 'agendar', component: AgendamientoAutonomo }, // Leyder
];
