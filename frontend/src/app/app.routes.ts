import { inject } from '@angular/core';
import { Routes } from '@angular/router';
import { AuthService } from './core/auth/auth.service';
import { authGuard, guestGuard, roleGuard } from './core/guards/auth-guards';
import { Shell } from './layout/shell/shell';

export const routes: Routes = [
  {
    path: 'login',
    canActivate: [guestGuard],
    loadComponent: () => import('./features/auth/login/login').then((m) => m.Login),
  },
  {
    path: 'registro',
    canActivate: [guestGuard],
    loadComponent: () => import('./features/auth/registro/registro').then((m) => m.Registro),
  },
  {
    path: '',
    component: Shell,
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: () => inject(AuthService).homeUrl() },
      {
        path: 'paciente',
        canActivate: [roleGuard(['paciente'])],
        loadChildren: () => import('./features/patient/patient.routes').then((m) => m.patientRoutes),
      },
      {
        path: 'appointments',
        loadChildren: () =>
          import('./features/appointments/appointments.routes').then((m) => m.appointmentsRoutes),
      },
      {
        path: 'configuration',
        canActivate: [roleGuard(['administrador'])],
        loadChildren: () =>
          import('./features/configuration/configuration.routes').then(
            (m) => m.configurationRoutes,
          ),
      },
    ],
  },
  { path: '**', redirectTo: '' },
];
