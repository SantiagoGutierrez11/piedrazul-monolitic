import { Component, booleanAttribute, input } from '@angular/core';

// Molécula: encabezado de una pantalla. Con `ruta` muestra la miga de pan (Administración / ...)
// y con el contenido proyectado muestra a la derecha las acciones principales de la pantalla.
@Component({
  selector: 'app-page-header',
  host: { '[class.grande]': 'grande()' },
  template: `
    @if (ruta()) {
      <p class="breadcrumb">{{ ruta() }}</p>
      <h1>{{ titulo() }}</h1>
      @if (subtitulo()) {
        <p class="subtitle">{{ subtitulo() }}</p>
      }
    } @else {
      <header class="panel-header">
        <div>
          <h1>{{ titulo() }}</h1>
          @if (subtitulo()) {
            <p class="subtitle">{{ subtitulo() }}</p>
          }
        </div>
        <div class="acciones"><ng-content /></div>
      </header>
    }
  `,
  styles: `
    :host {
      display: block;
    }

    .panel-header {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      justify-content: space-between;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .panel-header h1 {
      margin-bottom: 0.25rem;
    }

    .panel-header .subtitle {
      margin: 0;
    }

    .acciones {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
    }

    .acciones:empty {
      display: none;
    }

    :host(.grande) h1 {
      font-size: 2.1rem;
    }

    :host(.grande) .subtitle {
      font-size: 1.02rem;
    }
  `,
})
export class PageHeader {
  readonly titulo = input.required<string>();
  readonly subtitulo = input('');
  readonly ruta = input('');
  // Título y subtítulo un poco más grandes, para la pantalla de inicio.
  readonly grande = input(false, { transform: booleanAttribute });
}
