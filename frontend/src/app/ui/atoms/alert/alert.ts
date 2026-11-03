import { Component, computed, input } from '@angular/core';

export type AlertTone = 'ok' | 'error' | 'aviso' | 'info';

// Átomo: mensaje corto con el resultado de una acción (éxito, error, aviso o información).
// El propio elemento lleva la clase `alert`, así cada pantalla puede ajustar sus márgenes.
@Component({
  selector: 'app-alert',
  template: '<ng-content />',
  host: {
    class: 'alert',
    '[class.ok]': "tono() === 'ok'",
    '[class.error]': "tono() === 'error'",
    '[class.aviso]': "tono() === 'aviso'",
    '[class.info]': "tono() === 'info'",
    '[attr.role]': 'rol()',
  },
  styles: `
    :host {
      display: block;
      margin-top: 1rem;
      padding: 0.7rem 0.95rem;
      border-radius: var(--radius-sm);
      font-size: 0.9rem;
    }

    :host(.ok) {
      color: var(--color-success);
      background: var(--color-success-soft);
    }

    :host(.error) {
      color: var(--color-danger);
      background: var(--color-danger-soft);
    }

    :host(.aviso) {
      color: var(--color-warning);
      background: var(--color-warning-soft);
    }

    :host(.info) {
      color: var(--color-primary-dark);
      background: var(--color-primary-soft);
    }
  `,
})
export class Alert {
  readonly tono = input<AlertTone>('info');

  // Los errores se anuncian de inmediato a los lectores de pantalla; los éxitos, sin interrumpir.
  protected readonly rol = computed(() => {
    switch (this.tono()) {
      case 'error':
        return 'alert';
      case 'ok':
        return 'status';
      default:
        return null;
    }
  });
}
