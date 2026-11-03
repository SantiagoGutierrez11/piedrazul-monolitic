import { Component, booleanAttribute, input } from '@angular/core';

// Molécula: etiqueta + campo + mensaje de error. El campo (input o select) y su ayuda se proyectan
// dentro; lo que lleve el atributo `etiquetaExtra` (por ejemplo un ícono de ayuda) queda junto a la etiqueta.
@Component({
  selector: 'app-form-field',
  host: { class: 'field' },
  template: `
    <label [attr.for]="idControl()">
      {{ etiqueta() }}
      @if (obligatorio()) {
        <span class="required">*</span>
      }
      <ng-content select="[etiquetaExtra]" />
    </label>

    <ng-content />

    @if (error()) {
      <p class="field-error">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7.5v5.5M12 16.5v.01" stroke-linecap="round" />
        </svg>
        {{ error() }}
      </p>
    }
  `,
  styles: `
    :host {
      display: block;
    }

    label {
      display: flex;
      align-items: center;
    }

    .required {
      margin-left: 0.15rem;
    }

    .field-error svg {
      width: 0.95rem;
      height: 0.95rem;
      flex-shrink: 0;
    }
  `,
})
export class FormField {
  readonly etiqueta = input.required<string>();
  // Identificador del campo proyectado: une la etiqueta con su campo.
  readonly idControl = input.required<string>();
  readonly obligatorio = input(false, { transform: booleanAttribute });
  // Mensaje de error; vacío cuando el campo es válido o todavía no se debe avisar.
  readonly error = input('');
}
