import { Component, signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { FormField } from './form-field';

@Component({
  imports: [FormField],
  template: `
    <app-form-field etiqueta="Correo" idControl="correo" obligatorio [error]="error()">
      <span etiquetaExtra class="ayuda">?</span>
      <input id="correo" />
    </app-form-field>
    <app-form-field etiqueta="Segundo nombre" idControl="segundo">
      <input id="segundo" />
    </app-form-field>
  `,
})
class Anfitrion {
  readonly error = signal('');
}

describe('FormField', () => {
  function render() {
    const fixture = TestBed.createComponent(Anfitrion);
    fixture.detectChanges();
    const pagina = fixture.nativeElement as HTMLElement;
    return { fixture, pagina, campos: pagina.querySelectorAll<HTMLElement>('app-form-field') };
  }

  it('links the label to the projected control and marks required fields', () => {
    const [correo, segundo] = [...render().campos];

    expect(correo.classList).toContain('field');
    expect(correo.querySelector('label')!.getAttribute('for')).toBe('correo');
    expect(correo.querySelector('label')!.textContent).toContain('Correo');
    expect(correo.querySelector('.required')).not.toBeNull();
    expect(correo.querySelector('input#correo')).not.toBeNull();
    expect(segundo.querySelector('.required')).toBeNull();
  });

  it('keeps the extra content next to the label', () => {
    const [correo] = [...render().campos];

    expect(correo.querySelector('label .ayuda')).not.toBeNull();
  });

  it('shows the error message only when there is one', () => {
    const { fixture, campos } = render();
    const [correo] = [...campos];

    expect(correo.querySelector('.field-error')).toBeNull();

    fixture.componentInstance.error.set('El correo es obligatorio');
    fixture.detectChanges();

    expect(correo.querySelector('.field-error')!.textContent).toContain('El correo es obligatorio');
  });
});
