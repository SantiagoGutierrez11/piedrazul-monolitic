import { Component, computed, input } from '@angular/core';

// Átomo: etiqueta con el estado de una cita. El color depende del estado (agendada, reagendada,
// atendida, cancelada) y el texto que se muestra lo pone quien lo usa.
@Component({
  selector: 'app-status-badge',
  template: '<ng-content />',
  host: {
    class: 'badge',
    '[class]': 'variante()',
  },
  styles: `
    :host {
      display: inline-block;
      padding: 0.3rem 0.9rem;
      border: 1px solid transparent;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 500;
    }

    :host(.badge--agendada) {
      color: var(--color-success);
      background: var(--color-success-soft);
      border-color: #a7f3d0;
    }

    :host(.badge--reagendada) {
      color: var(--color-primary);
      background: var(--color-primary-soft);
      border-color: #bfdbfe;
    }

    :host(.badge--atendida) {
      color: var(--color-text-muted);
      background: #f1f5f9;
      border-color: #e2e8f0;
    }

    :host(.badge--cancelada) {
      color: var(--color-danger);
      background: var(--color-danger-soft);
      border-color: #fecaca;
    }
  `,
})
export class StatusBadge {
  // Estado tal como lo entrega el backend, por ejemplo `AGENDADA`.
  readonly estado = input.required<string>();

  protected readonly variante = computed(() => `badge--${this.estado().toLowerCase()}`);
}
