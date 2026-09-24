import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ConfigurationService } from '../services/configuration.service';

@Component({
  selector: 'app-configuracion-global',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './configuracion-global.html',
  styleUrl: './configuracion-global.scss',
})
export class ConfiguracionGlobal implements OnInit {
  private readonly configurationService = inject(ConfigurationService);
  private readonly router = inject(Router);

  readonly weeks = signal(4);
  readonly saving = signal(false);
  readonly message = signal('');
  readonly error = signal('');

  ngOnInit(): void {
    this.configurationService.getGlobalConfiguration().subscribe({
      next: (data) => this.weeks.set(data.weeks),
      error: () => this.error.set('No se pudo cargar la configuración actual.'),
    });
  }

  cancelar(): void {
    this.router.navigate(['/configuration']);
  }

  guardar(): void {
    this.saving.set(true);
    this.message.set('');
    this.error.set('');

    this.configurationService.updateAppointmentWindow(this.weeks()).subscribe({
      next: () => {
        this.message.set('Configuración guardada.');
        this.saving.set(false);
      },
      error: (response) => {
        this.error.set(response?.error?.message ?? 'No se pudo guardar la configuración.');
        this.saving.set(false);
      },
    });
  }
}
