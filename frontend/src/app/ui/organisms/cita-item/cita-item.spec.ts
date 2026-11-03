import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { Appointment } from '../../../features/appointments/models/appointment.model';
import { CitaItem } from './cita-item';

const CITA: Appointment = {
  appointmentId: 7,
  patientId: 1,
  patientName: null,
  patientPhone: null,
  doctorId: 1,
  doctorName: 'Dra. Laura Muñoz',
  serviceType: 'FISIOTERAPIA',
  date: '2026-11-03',
  startTime: '09:00:00',
  endTime: '09:30:00',
  reason: 'Terapia de rodilla',
  status: 'AGENDADA',
};

@Component({
  imports: [CitaItem],
  template: `
    <app-cita-item [cita]="cita" />
    <app-cita-item
      [cita]="cancelada"
      [cancelable]="true"
      (cancelar)="pedidas.push($event.appointmentId)"
    />
  `,
})
class Anfitrion {
  readonly cita = CITA;
  readonly cancelada: Appointment = { ...CITA, appointmentId: 8, status: 'CANCELADA' };
  readonly pedidas: number[] = [];
}

describe('CitaItem', () => {
  function render() {
    const fixture = TestBed.createComponent(Anfitrion);
    fixture.detectChanges();
    return {
      fixture,
      items: [
        ...(fixture.nativeElement as HTMLElement).querySelectorAll<HTMLElement>('app-cita-item'),
      ],
    };
  }

  it('shows the date, the time, the doctor, the service and the status', () => {
    const [item] = render().items;

    expect(item.textContent).toContain('Martes 3 de noviembre');
    expect(item.textContent).toContain('9:00 a. m.');
    expect(item.textContent).toContain('Dra. Laura Muñoz, Fisioterapia');
    expect(item.querySelector('app-status-badge')!.classList).toContain('badge--agendada');
    expect(item.querySelector('app-status-badge')!.textContent).toContain('Agendada');
  });

  it('only offers to cancel when the list allows it', () => {
    const [sinBoton, conBoton] = render().items;

    expect(sinBoton.querySelector('button.cancelar')).toBeNull();
    expect(conBoton.querySelector('button.cancelar')).not.toBeNull();
  });

  it('asks to cancel the appointment it shows', () => {
    const { fixture, items } = render();

    items[1].querySelector<HTMLButtonElement>('button.cancelar')!.click();

    expect(fixture.componentInstance.pedidas).toEqual([8]);
  });
});
