import { Routes } from '@angular/router';
import { ListarCitas } from './listar-citas/listar-citas';

// Montado en app.routes.ts bajo /appointments (lazy-loaded).
export const appointmentsRoutes: Routes = [{ path: 'listar', component: ListarCitas }];
