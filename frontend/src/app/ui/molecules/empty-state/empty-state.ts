import { Component, booleanAttribute, input } from '@angular/core';

// Molécula: mensaje cuando no hay datos que mostrar o todavía se están cargando.
// Con `tarjeta` ocupa su propia tarjeta; sin ella va dentro de un bloque que ya es una tarjeta.
@Component({
  selector: 'app-empty-state',
  host: {
    '[class.vacio]': '!tarjeta()',
    '[class.card]': 'tarjeta()',
    '[class.empty-state]': 'tarjeta()',
  },
  template: '<ng-content />',
  styles: `
    :host(.vacio) {
      display: block;
      margin: 0;
      padding: 1.5rem;
      color: var(--color-text-muted);
    }

    :host(.empty-state) {
      display: block;
      padding: 3rem 1rem;
      color: var(--color-text-muted);
      text-align: center;
    }
  `,
})
export class EmptyState {
  readonly tarjeta = input(false, { transform: booleanAttribute });
}
