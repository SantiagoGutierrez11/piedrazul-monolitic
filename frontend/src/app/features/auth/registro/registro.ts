import { NgTemplateOutlet } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, HostListener, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { mensajeDeError } from '../../../shared/error-messages';
import { GENEROS, Genero, TIPOS_DOCUMENTO, TipoDocumento } from '../models/registro.model';
import { RegistroService } from '../services/registro.service';
import { Campo, formularioValido, hoyLocal, validarCampo } from './registro.validaciones';
import { Alert } from '../../../ui/atoms/alert/alert';
import { FormField } from '../../../ui/molecules/form-field/form-field';
import { AuthLayout } from '../../../ui/templates/auth-layout/auth-layout';

@Component({
  selector: 'app-registro',
  imports: [ReactiveFormsModule, RouterLink, NgTemplateOutlet, Alert, FormField, AuthLayout],
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

  // Las reglas de cada campo están en registro.validaciones.ts. Angular marca el campo como
  // "tocado" al perder el foco; desde ese momento se muestra su error.
  readonly form = inject(NonNullableFormBuilder).group({
    firstName: '',
    middleName: '',
    lastName: '',
    secondLastName: '',
    email: '',
    phone: '',
    birthDate: '',
    gender: '' as Genero | '',
    documentType: '' as TipoDocumento | '',
    documentNumber: '',
    password: '',
    confirmPassword: '',
  });

  mensaje(campo: Campo): string {
    return validarCampo(campo, this.form.getRawValue());
  }

  mostrarError(campo: Campo): boolean {
    const tocado = this.form.controls[campo].touched || this.intentoEnviar();
    return tocado && this.mensaje(campo) !== '';
  }

  crearCuenta(): void {
    this.intentoEnviar.set(true);
    this.error.set('');
    if (!formularioValido(this.form.getRawValue())) {
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
