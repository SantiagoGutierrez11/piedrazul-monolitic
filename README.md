# Piedrazul

Sistema de agendamiento de citas médicas. Proyecto de Ingeniería de Software 3,
Universidad del Cauca, 2026.2.

Es un monolito modular: un solo backend en FastAPI (Python) dividido en módulos
independientes, un frontend en Angular, PostgreSQL como base de datos y Keycloak para el
inicio de sesión.

## Integrantes

| Integrante | Historia de usuario principal |
|---|---|
| Leyder Cerón | Agendamiento autónomo de citas |
| Andrea Gómez | Listar citas |
| Santiago Gutiérrez | Configuración del sistema |

## Cómo ejecutarlo

Solo se necesita Docker. Desde la carpeta del proyecto:

```bash
docker compose up --build -d
```

Espera unos 30 segundos a que Keycloak arranque y carga los datos de ejemplo:

```bash
docker compose exec backend python -m app.seed
```

Luego abre http://localhost:4200

| Servicio | Dirección |
|---|---|
| Aplicación | http://localhost:4200 |
| API y su documentación | http://localhost:8000/docs |
| Keycloak (consola, `admin` / `admin`) | http://localhost:8080 |

Para apagar todo usa `docker compose down`. Si cambió la estructura de la base de datos,
usa `docker compose down -v` (borra los datos) y vuelve a cargar el seed.

### Usuarios de prueba

El rol se detecta solo al iniciar sesión.

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | `admin@piedrazul.com` | `admin123` |
| Agendador | `agendador@piedrazul.com` | `agendador123` |
| Médico | `medico@piedrazul.com` | `medico123` |
| Paciente | `paciente@piedrazul.com` | `paciente123` |

También se puede crear una cuenta de paciente nueva desde **Regístrate**.

## Qué puede hacer cada rol

- **Paciente:** registrarse, agendar su propia cita en cuatro pasos (servicio,
  profesional, día y hora), ver su próxima cita y su historial, y cancelar.
- **Médico:** ver su día (pacientes, atendidos y pendientes) y marcar citas como
  atendidas. Al atender puede autorizar un servicio especializado al paciente.
- **Agendador:** ver la agenda del día de todos los profesionales, filtrar por
  profesional y fecha, y cancelar citas.
- **Administrador:** ver el resumen general y configurar la ventana de agendamiento y el
  horario de cada profesional.

## Reglas al agendar una cita

Antes de guardar una cita, el backend revisa en este orden:

1. Los datos están completos, la fecha no es pasada y el motivo tiene al menos 5 caracteres.
2. No es un festivo en Colombia.
3. El paciente y el profesional existen, y el profesional está activo.
4. El profesional atiende el servicio pedido.
5. El paciente no tiene otra cita activa.
6. La fecha está dentro de la ventana de agendamiento (4 semanas por defecto).
7. La hora está dentro del horario del profesional.
8. Fisioterapia, Quiropraxia y Terapia Neural necesitan una autorización de Medicina General.
9. La franja no está ocupada por otra cita.

Si alguna falla, la cita no se guarda y el usuario ve el motivo.

## Estructura

```
backend/app/
├── core/          configuración, base de datos, seguridad y eventos
├── shared/        reloj y festivos de Colombia
└── modules/
    ├── appointment/     citas: agendar, listar, cancelar y atender
    ├── medical_staff/   profesionales y disponibilidad
    ├── configuration/   ventana de agendamiento y horarios
    ├── patient/         registro y perfil del paciente
    └── identity/        inicio de sesión con Keycloak

frontend/src/app/
├── core/          sesión, roles, guards e interceptor del token
├── layout/        barra lateral según el rol
└── features/      pantallas de cada módulo
```

Cada módulo del backend tiene cuatro capas: `api`, `application`, `domain` e
`infrastructure`. Cada módulo usa su propio schema en PostgreSQL y se comunica con
los demás a través de fachadas (`Directory`), sin leer tablas ajenas.

### Patrones de diseño usados

| Patrón | Dónde |
|---|---|
| Strategy y Chain of Responsibility | `appointment/domain/validators/` y `application/scheduling/validation_chain.py` |
| Template Method | `appointment/application/scheduling/base.py` |
| Builder y Director | `appointment/domain/builder/` |
| Factory Method | `medical_staff/domain/factory/availability_generator.py` |
| Fachada entre módulos | `application/directory.py` de appointment, medical_staff, patient y configuration |
| Puertos (interfaces) | `appointment/domain/ports.py` e `identity/domain/ports.py` |

## Pruebas

Backend:

```bash
cd backend
pip install -r requirements.txt
pytest
```

Frontend:

```bash
cd frontend
npm install
npm test
```

Las pruebas del backend no necesitan Keycloak ni PostgreSQL: usan tokens de prueba, una
base en memoria y una fecha fija.

## Desarrollo sin Docker

Backend (usa SQLite si no hay `DATABASE_URL`; Keycloak sí debe estar corriendo con
`docker compose up -d keycloak`):

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm start
```
