import { Component, booleanAttribute, input } from '@angular/core';

// Plantilla de las pantallas públicas (inicio de sesión y registro): fondo centrado, marca de
// Piedrazul arriba y, debajo, lo que cada pantalla proyecte (la tarjeta del formulario y su pie).
@Component({
  selector: 'app-auth-layout',
  host: { style: 'display: block' },
  template: `
    <div class="auth-page">
      <header class="auth-brand" [class.compact]="compacto()">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path
              d="M12 20s-7-4.35-7-9a4 4 0 0 1 7-2.65A4 4 0 0 1 19 11c0 4.65-7 9-7 9Z"
              stroke-linejoin="round"
            />
            <path
              d="M6 12.5h3l1.5-2.5 2 4 1.5-2.5h3"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        @if (compacto()) {
          <h1>{{ titulo() }}</h1>
        } @else {
          <strong>Piedrazul</strong>
        }
        <small>{{ subtitulo() }}</small>
      </header>

      <ng-content />
    </div>
  `,
  styles: `
    .auth-page {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 2.5rem 1rem;
    }

    .auth-brand {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.15rem;
      margin-bottom: 1.5rem;
      text-align: center;
    }

    .brand-mark {
      display: grid;
      place-items: center;
      width: 3.25rem;
      height: 3.25rem;
      margin-bottom: 0.65rem;
      border-radius: 14px;
      background: var(--color-primary);
      color: #fff;
    }

    .brand-mark svg {
      width: 1.9rem;
      height: 1.9rem;
    }

    strong {
      font-size: 1.35rem;
      font-weight: 700;
    }

    small {
      font-size: 0.85rem;
      color: var(--color-text-muted);
    }

    /* Versión compacta del registro: marca más pequeña y título en lugar del nombre. */
    .auth-brand.compact {
      margin-bottom: 1.25rem;
    }

    .compact .brand-mark {
      width: 2.6rem;
      height: 2.6rem;
      margin-bottom: 0.5rem;
      border-radius: 11px;
    }

    .compact .brand-mark svg {
      width: 1.5rem;
      height: 1.5rem;
    }

    .compact h1 {
      margin: 0;
      font-size: 1.6rem;
    }
  `,
})
export class AuthLayout {
  readonly titulo = input('');
  readonly subtitulo = input('');
  // Muestra el título (h1) en lugar del nombre de la clínica, con la marca más pequeña.
  readonly compacto = input(false, { transform: booleanAttribute });
}
