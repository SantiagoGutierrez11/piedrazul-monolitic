import { Routes } from '@angular/router';
import { roleGuard } from '../../core/guards/auth-guards';
import { PanelAdmin } from './panel-admin/panel-admin';
import { PanelAgenda } from './panel-agenda/panel-agenda';
import { PanelMedico } from './panel-medico/panel-medico';

// Montado en app.routes.ts bajo /panel: pantalla inicial de cada rol del personal.
export const dashboardRoutes: Routes = [
  { path: 'medico', component: PanelMedico, canActivate: [roleGuard(['medico'])] },
  { path: 'agenda', component: PanelAgenda, canActivate: [roleGuard(['agendador'])] },
  { path: 'admin', component: PanelAdmin, canActivate: [roleGuard(['administrador'])] },
];
