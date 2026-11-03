import { Component, signal } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ConfirmDialog } from './confirm-dialog';

@Component({
  imports: [ConfirmDialog],
  template: `
    <app-confirm-dialog
      titulo="Cancelar cita"
      mensaje="La cita quedará cancelada."
      textoConfirmar="Sí, cancelar"
      [ocupado]="ocupado()"
      (confirmar)="confirmadas = confirmadas + 1"
      (cancelar)="canceladas = canceladas + 1"
    />
  `,
})
class Anfitrion {
  readonly ocupado = signal(false);
  confirmadas = 0;
  canceladas = 0;
}

describe('ConfirmDialog', () => {
  let fixture: ComponentFixture<Anfitrion>;
  const pagina = () => fixture.nativeElement as HTMLElement;
  const botones = () => [
    ...pagina().querySelectorAll<HTMLButtonElement>('[role="alertdialog"] button'),
  ];

  beforeEach(() => {
    fixture = TestBed.createComponent(Anfitrion);
    fixture.detectChanges();
  });

  it('shows the title, the message and the confirm text it was given', () => {
    const dialogo = pagina().querySelector('[role="alertdialog"]')!;

    expect(dialogo.textContent).toContain('Cancelar cita');
    expect(dialogo.textContent).toContain('La cita quedará cancelada.');
    expect(botones().map((boton) => boton.textContent!.trim())).toEqual(['Volver', 'Sí, cancelar']);
  });

  it('emits the confirmation and the cancellation from its buttons', () => {
    const [volver, confirmar] = botones();

    confirmar.click();
    volver.click();

    expect(fixture.componentInstance.confirmadas).toBe(1);
    expect(fixture.componentInstance.canceladas).toBe(1);
  });

  it('closes with Escape unless it is busy', () => {
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    expect(fixture.componentInstance.canceladas).toBe(1);

    fixture.componentInstance.ocupado.set(true);
    fixture.detectChanges();
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));

    expect(fixture.componentInstance.canceladas).toBe(1);
    expect(botones().every((boton) => boton.disabled)).toBe(true);
  });
});
