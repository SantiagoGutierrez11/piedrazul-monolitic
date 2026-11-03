import { Component, input } from '@angular/core';

export type StatTone = 'ok' | 'warn' | 'danger';

// Molécula: tarjeta con una cifra y su etiqueta (por ejemplo "Pacientes hoy: 12").
// El contenido proyectado se muestra debajo de la cifra, como detalle.
@Component({
  selector: 'app-stat-card',
  host: { class: 'card stat' },
  template: `
    <small>{{ etiqueta() }}</small>
    <strong [class]="tono() ?? ''">{{ valor() }}</strong>
    <ng-content />
  `,
  styles: `
    :host(.stat) {
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      padding: 1.1rem 1.25rem;
    }

    small {
      font-size: 0.85rem;
      color: var(--color-text-muted);
    }

    strong {
      font-size: 1.75rem;
      letter-spacing: -0.02em;
    }

    strong.ok {
      color: var(--color-success);
    }

    strong.warn {
      color: var(--color-warning);
    }

    strong.danger {
      color: var(--color-danger);
    }
  `,
})
export class StatCard {
  readonly etiqueta = input.required<string>();
  readonly valor = input.required<string | number>();
  readonly tono = input<StatTone | null>(null);
}
