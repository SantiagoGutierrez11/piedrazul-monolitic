import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'appointments/listar', pathMatch: 'full' },
  {
    path: 'login',
    loadChildren: () => import('./features/auth/auth.routes').then((m) => m.authRoutes),
  },
  {
    path: 'appointments',
    loadChildren: () =>
      import('./features/appointments/appointments.routes').then((m) => m.appointmentsRoutes),
  },
];
