import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

// Placeholder mínimo, sin Keycloak todavía (eso llega en el Corte 2).
// Necesario para que las features protegidas (listar-citas, agendamiento, configuración)
// tengan algo que las anteceda.
@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {}
