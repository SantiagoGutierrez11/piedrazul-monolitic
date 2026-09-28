import { NgTemplateOutlet } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, HostListener, inject, signal } from '@angular/core';
import {
  AbstractControl,
  NonNullableFormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { mensajeDeError } from '../../../shared/error-messages';
import { GENEROS, Genero, TIPOS_DOCUMENTO, TipoDocumento } from '../models/registro.model';
import { RegistroService } from '../services/registro.service';

const NOMBRE = /^[A-Za-zÀ-ÿ' -]*$/;
const DOCUMENTO = /^[A-Za-z0-9]{5,15}$/;

type Campo = keyof Registro['form']['controls'];

@Component({
  selector: 'app-registro',
  imports: [ReactiveFormsModule, RouterLink, NgTemplateOutlet],
  templateUrl: './registro.html',
  styleUrls: ['../auth-page.scss', './registro.scss'],
})
export class Registro {
  private readonly registroService = inject(RegistroService);
  private readonly router = inject(Router);

  readonly generos = GENEROS;
  readonly tiposDocumento = TIPOS_DOCUMENTO;
  readonly hoy = hoyLocal();

  readonly verPassword = signal(true);
  readonly verConfirmacion = signal(true);
  readonly enviando = signal(false);
  readonly error = signal('');
  readonly cuentaCreada = signal(false);
  private readonly intentoEnviar = signal(false);

  readonly form = inject(NonNullableFormBuilder).group(
    {
      firstName: ['', [Validators.required, Validators.minLength(2), Validators.pattern(NOMBRE)]],
      middleName: ['', Validators.pattern(NOMBRE)],
      lastName: ['', [Validators.required, Validators.minLength(2), Validators.pattern(NOMBRE)]],
      secondLastName: ['', Validators.pattern(NOMBRE)],
      email: ['', [Validators.required, Validators.email]],
      phone: ['', [Validators.required, telefonoValido]],
      birthDate: ['', [Validators.required, fechaNoFutura]],
      gender: ['' as Genero | '', Validators.required],
      documentType: ['' as TipoDocumento | '', Validators.required],
      documentNumber: ['', [Validators.required, Validators.pattern(DOCUMENTO)]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required],
    },
    { validators: contrasenasIguales },
  );

  mostrarError(campo: Campo): boolean {
    const control = this.form.controls[campo];
    const invalido =
      control.invalid || (campo === 'confirmPassword' && this.form.hasError('contrasenasDistintas'));
    return invalido && (control.touched || this.intentoEnviar());
  }

  mensaje(campo: Campo): string {
    const errores = this.form.controls[campo].errors ?? {};
    if (errores['required']) {
      return REQUERIDOS[campo];
    }
    if (campo === 'confirmPassword') {
      return 'Las contraseñas no coinciden';
    }
    return FORMATOS[campo];
  }

  crearCuenta(): void {
    this.intentoEnviar.set(true);
    this.error.set('');
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const datos = this.form.getRawValue();
    this.enviando.set(true);
    this.registroService
      .registrar({
        ...datos,
        email: datos.email.trim(),
        gender: datos.gender as Genero,
        documentType: datos.documentType as TipoDocumento,
      })
      .subscribe({
        next: () => {
          this.enviando.set(false);
          this.cuentaCreada.set(true);
        },
        error: (response: HttpErrorResponse) => {
          this.enviando.set(false);
          this.error.set(mensajeDeError(response, 'No fue posible crear la cuenta.'));
        },
      });
  }

  @HostListener('document:keydown.escape')
  cerrarConfirmacion(): void {
    if (this.cuentaCreada()) {
      this.router.navigate(['/login'], { state: { email: this.form.controls.email.value.trim() } });
    }
  }
}

const REQUERIDOS: Record<Campo, string> = {
  firstName: 'El primer nombre es obligatorio',
  middleName: '',
  lastName: 'El primer apellido es obligatorio',
  secondLastName: '',
  email: 'El correo electrónico es obligatorio',
  phone: 'El teléfono es obligatorio',
  birthDate: 'La fecha de nacimiento es obligatoria',
  gender: 'Selecciona un género',
  documentType: 'Selecciona el tipo de documento',
  documentNumber: 'El número de documento es obligatorio',
  password: 'La contraseña es obligatoria',
  confirmPassword: 'Confirma tu contraseña',
};

const FORMATOS: Record<Campo, string> = {
  firstName: 'Usa solo letras (mínimo 2)',
  middleName: 'Usa solo letras',
  lastName: 'Usa solo letras (mínimo 2)',
  secondLastName: 'Usa solo letras',
  email: 'Ingresa un correo válido, por ejemplo nombre@correo.com',
  phone: 'Ingresa entre 7 y 15 dígitos, por ejemplo 300 123 4567',
  birthDate: 'La fecha no puede ser posterior a hoy',
  gender: '',
  documentType: '',
  documentNumber: 'Usa entre 5 y 15 números o letras, sin puntos ni espacios',
  password: 'La contraseña debe tener mínimo 8 caracteres',
  confirmPassword: 'Las contraseñas no coinciden',
};

function telefonoValido(control: AbstractControl<string>): ValidationErrors | null {
  const valor = control.value.replace(/[\s-]/g, '');
  return !valor || /^\+?\d{7,15}$/.test(valor) ? null : { telefono: true };
}

function fechaNoFutura(control: AbstractControl<string>): ValidationErrors | null {
  return control.value && control.value > hoyLocal()
    ? { fechaFutura: true }
    : null;
}

const contrasenasIguales: ValidatorFn = (grupo) => {
  const password = grupo.get('password')?.value;
  const confirmacion = grupo.get('confirmPassword')?.value;
  return confirmacion && password !== confirmacion ? { contrasenasDistintas: true } : null;
};

/** Fecha de hoy (AAAA-MM-DD) en la zona horaria del usuario, como la muestra el calendario. */
function hoyLocal(): string {
  const ahora = new Date();
  return new Date(ahora.getTime() - ahora.getTimezoneOffset() * 60_000).toISOString().slice(0, 10);
}
