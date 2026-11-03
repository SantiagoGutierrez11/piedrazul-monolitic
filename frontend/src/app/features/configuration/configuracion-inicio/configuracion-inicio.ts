import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { PageHeader } from '../../../ui/molecules/page-header/page-header';

@Component({
  selector: 'app-configuracion-inicio',
  standalone: true,
  imports: [RouterLink, PageHeader],
  templateUrl: './configuracion-inicio.html',
  styleUrl: './configuracion-inicio.scss',
})
export class ConfiguracionInicio {}
