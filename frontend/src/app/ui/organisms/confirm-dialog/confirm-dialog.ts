import { Component, HostListener, input, output } from '@angular/core';

// Diálogo para confirmar una acción que no se puede deshacer (p. ej. cancelar una cita).
@Component({
  selector: 'app-confirm-dialog',
  template: `
    <div class="fondo" (click)="cancelar.emit()">
      <div
        class="dialogo"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="dialogo-titulo"
        aria-describedby="dialogo-mensaje"
        (click)="$event.stopPropagation()"
      >
        <h2 id="dialogo-titulo">{{ titulo() }}</h2>
        <p id="dialogo-mensaje">{{ mensaje() }}</p>
        <div class="acciones">
          <button type="button" class="secondary" (click)="cancelar.emit()" [disabled]="ocupado()">
            {{ textoCancelar() }}
          </button>
          <button type="button" class="peligro" (click)="confirmar.emit()" [disabled]="ocupado()">
            {{ ocupado() ? 'Un momento...' : textoConfirmar() }}
          </button>
        </div>
      </div>
    </div>
  `,
  styles: `
    .fondo {
      position: fixed;
      inset: 0;
      z-index: 100;
      display: grid;
      place-items: center;
      padding: 1rem;
      background: rgba(15, 23, 42, 0.35);
    }

    .dialogo {
      width: 100%;
      max-width: 27rem;
      padding: 1.75rem;
      background: var(--color-surface);
      border-radius: var(--radius-lg);
      box-shadow: 0 20px 45px rgba(15, 23, 42, 0.18);
    }

    h2 {
      margin: 0 0 0.6rem;
      font-size: 1.2rem;
    }

    p {
      margin: 0 0 1.5rem;
      color: var(--color-text-muted);
    }

    .acciones {
      display: flex;
      justify-content: flex-end;
      gap: 0.75rem;
    }

    .peligro {
      background: var(--color-danger);

      &:hover:not(:disabled) {
        background: #b91c1c;
      }
    }
  `,
})
export class ConfirmDialog {
  readonly titulo = input.required<string>();
  readonly mensaje = input.required<string>();
  readonly textoConfirmar = input('Confirmar');
  readonly textoCancelar = input('Volver');
  readonly ocupado = input(false);

  readonly confirmar = output<void>();
  readonly cancelar = output<void>();

  @HostListener('document:keydown.escape')
  alPresionarEscape(): void {
    if (!this.ocupado()) {
      this.cancelar.emit();
    }
  }
}
