import { Routes } from '@angular/router';
import { ConfiguracionGlobal } from './configuracion-global/configuracion-global';
import { ConfiguracionProfesional } from './configuracion-profesional/configuracion-profesional';

// Montado en app.routes.ts bajo /configuration (lazy-loaded).
export const configurationRoutes: Routes = [
  { path: 'global', component: ConfiguracionGlobal },
  { path: 'profesional', component: ConfiguracionProfesional },
];
