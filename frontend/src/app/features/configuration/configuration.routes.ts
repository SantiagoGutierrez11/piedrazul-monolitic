import { Routes } from '@angular/router';
import { ConfiguracionInicio } from './configuracion-inicio/configuracion-inicio';
import { ConfiguracionGlobal } from './configuracion-global/configuracion-global';
import { ConfiguracionProfesional } from './configuracion-profesional/configuracion-profesional';

// Montado en app.routes.ts bajo /configuration (lazy-loaded).
export const configurationRoutes: Routes = [
  { path: '', component: ConfiguracionInicio },
  { path: 'global', component: ConfiguracionGlobal },
  { path: 'profesional', component: ConfiguracionProfesional },
];
