# ui: Atomic Design

Los componentes visuales reutilizables se organizan por tamaño, de lo más pequeño a lo más grande.
Cada pantalla de `features/` (las páginas) se arma combinando estas piezas.

```
ui/
├── atoms/        la pieza más pequeña, sin lógica de negocio
│   ├── alert/             mensaje de éxito, error, aviso o información        <app-alert>
│   └── status-badge/      etiqueta de color con el estado de una cita         <app-status-badge>
├── molecules/    pocos átomos trabajando juntos
│   ├── form-field/        etiqueta + campo + mensaje de error                 <app-form-field>
│   ├── page-header/       miga de pan, título, subtítulo y acciones           <app-page-header>
│   ├── stat-card/         cifra con su etiqueta                               <app-stat-card>
│   └── empty-state/       mensaje de "cargando" o "sin datos"                 <app-empty-state>
├── organisms/    secciones completas de la interfaz
│   ├── confirm-dialog/    diálogo para confirmar una acción                   <app-confirm-dialog>
│   └── cita-item/         fila de una cita con su estado y botón de cancelar  <app-cita-item>
└── templates/    la estructura general de una pantalla
    ├── shell/             barra lateral según el rol + contenido de la ruta   <app-shell>
    └── auth-layout/       fondo, marca y tarjeta de login y registro          <app-auth-layout>
```

Reglas:

- Un nivel solo usa los de abajo: una molécula puede usar átomos, pero un átomo no usa moléculas.
- `ui/` no hace llamadas al backend: las pantallas le pasan los datos con `input()`.
- Si dos pantallas necesitan el mismo elemento, se crea aquí en vez de copiarlo.
