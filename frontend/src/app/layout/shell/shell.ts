import { Component, computed, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ROLE_LABELS, Role } from '../../core/auth/auth.models';
import { AuthService } from '../../core/auth/auth.service';

// Estructura de las pantallas internas: barra lateral según el rol y el contenido de la ruta.
@Component({
  selector: 'app-shell',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './shell.html',
  styleUrl: './shell.scss',
})
export class Shell {
  private readonly auth = inject(AuthService);

  readonly user = this.auth.user;
  readonly isPatient = computed(() => this.auth.hasRole('paciente'));
  readonly initial = computed(() => this.user()?.fullName.charAt(0).toUpperCase() ?? '');
  readonly roleLabel = computed(() => {
    const roles = this.user()?.roles ?? [];
    return roles.map((role) => ROLE_LABELS[role]).join(' · ');
  });

  can(...roles: Role[]): boolean {
    return this.auth.hasRole(...roles);
  }

  logout(): void {
    this.auth.logout();
  }
}
