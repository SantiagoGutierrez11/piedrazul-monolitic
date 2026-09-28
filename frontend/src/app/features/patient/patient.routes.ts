import { Routes } from '@angular/router';
import { InicioPaciente } from './inicio/inicio';
import { MisCitas } from './mis-citas/mis-citas';

// Montado en app.routes.ts bajo /paciente (lazy-loaded, solo para el rol paciente).
export const patientRoutes: Routes = [
  { path: 'inicio', component: InicioPaciente },
  { path: 'citas', component: MisCitas },
];
