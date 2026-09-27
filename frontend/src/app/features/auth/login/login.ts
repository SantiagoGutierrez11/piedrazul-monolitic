import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthUser } from '../../../core/auth/auth.models';
import { AuthService } from '../../../core/auth/auth.service';
import { mensajeDeError } from '../error-messages';

type Perfil = 'paciente' | 'profesional';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrls: ['../auth-page.scss', './login.scss'],
})
export class Login {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  readonly perfil = signal<Perfil>('paciente');
  readonly verPassword = signal(false);
  readonly enviando = signal(false);
  readonly error = signal('');
  readonly aviso = signal('');
  private readonly intentoEnviar = signal(false);

  readonly form = inject(NonNullableFormBuilder).group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
    recordarme: false,
  });

  constructor() {
    // Datos que dejan otras pantallas al navegar hacia aquí (registro exitoso o sesión vencida).
    const estado = history.state ?? {};
    if (typeof estado.email === 'string') {
      this.form.controls.email.setValue(estado.email);
    }
    if (estado.sessionExpired) {
      this.aviso.set('Tu sesión expiró. Inicia sesión de nuevo para continuar.');
    }
  }

  seleccionarPerfil(perfil: Perfil): void {
    this.perfil.set(perfil);
    this.error.set('');
  }

  mostrarError(campo: 'email' | 'password'): boolean {
    const control = this.form.controls[campo];
    return control.invalid && (control.touched || this.intentoEnviar());
  }

  ingresar(): void {
    this.intentoEnviar.set(true);
    this.error.set('');
    this.aviso.set('');
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const { email, password, recordarme } = this.form.getRawValue();
    this.enviando.set(true);
    this.auth.login(email, password, recordarme).subscribe({
      next: (usuario) => {
        this.enviando.set(false);
        if (!this.correspondeAlPerfil(usuario)) {
          this.auth.logout({ redirect: false });
          this.error.set(
            this.perfil() === 'paciente'
              ? 'Esta cuenta es de un profesional. Ingresa desde la pestaña "Profesional".'
              : 'Esta cuenta es de un paciente. Ingresa desde la pestaña "Paciente".',
          );
          return;
        }
        this.router.navigateByUrl(this.auth.homeUrl());
      },
      error: (response: HttpErrorResponse) => {
        this.enviando.set(false);
        this.error.set(mensajeDeError(response, 'No fue posible iniciar sesión.'));
      },
    });
  }

  private correspondeAlPerfil(usuario: AuthUser): boolean {
    const esPaciente = usuario.roles.includes('paciente');
    return this.perfil() === 'paciente' ? esPaciente : usuario.roles.some((r) => r !== 'paciente');
  }
}
