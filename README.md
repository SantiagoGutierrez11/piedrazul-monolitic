# Piedrazul — Monolito Modular

> Sistema de agendamiento de citas médicas · 2026.2, Corte 1

**Piedrazul** es un sistema de agendamiento de citas médicas desarrollado como proyecto
académico para Ingeniería de Software 3. Este repositorio contiene la versión
**monolito modular**: un refactor de `../Mircoservicios/piedrazul` (arquitectura de
microservicios con Spring Boot + React) hacia un único desplegable con backend en
**FastAPI** (Python) y frontend en **Angular**, donde cada módulo de negocio conserva
la misma separación en capas — dominio, aplicación e infraestructura — que tenía como
microservicio independiente.

---

## Tabla de contenidos

- [Ejecutar con Docker](#ejecutar-con-docker)
- [Dueños por Corte 1](#dueños-por-corte-1)
- [Backend (FastAPI)](#backend-fastapi)
- [Frontend (Angular 22)](#frontend-angular-22-standalone-components)
- [Decisión de base de datos](#decisión-de-base-de-datos)

---

## Ejecutar con Docker

La forma más rápida de levantar todo (PostgreSQL + Keycloak + backend + frontend) sin
instalar Python ni Node:

```bash
docker compose up --build
```

| Servicio | URL |
|---|---|
| Frontend (Angular + nginx) | http://localhost:4200 |
| Backend (FastAPI) | http://localhost:8000 · docs en `/docs` |
| Keycloak | http://localhost:8080 · consola de administración con `admin` / `admin` |
| PostgreSQL | localhost:5432 (usuario/clave `postgres`) |

Keycloak tarda unos 30 segundos en quedar listo la primera vez: importa el realm
`piedrazul` desde `keycloak/realm-piedrazul.json`, con los cuatro roles (`paciente`,
`agendador`, `medico`, `administrador`), el cliente del backend y los usuarios de prueba.

Los schemas y tablas de cada módulo se crean solos al arrancar el backend. Para cargar
datos de ejemplo y poder ver el listado de citas:

```bash
docker compose exec backend python -m app.seed
```

Para bajar todo (agrega `-v` si además quieres borrar la base de datos):

```bash
docker compose down
```

> **Si ya tenías la base creada antes de la integración con Keycloak**, bórrala con
> `docker compose down -v` y vuelve a cargar los datos de ejemplo: la tabla de pacientes
> tiene columnas nuevas y el proyecto no usa migraciones.

### Usuarios de prueba

Solo para desarrollo. Todos inician sesión con su correo:

| Rol | Correo | Contraseña | Pestaña del login |
|---|---|---|---|
| Administrador | `admin@piedrazul.com` | `admin123` | Profesional |
| Agendador | `agendador@piedrazul.com` | `agendador123` | Profesional |
| Médico | `medico@piedrazul.com` | `medico123` | Profesional |
| Paciente | `paciente@piedrazul.com` | `paciente123` | Paciente |

El paciente de prueba corresponde a María García López de los datos de ejemplo. Cualquier
persona puede crear su propia cuenta de paciente desde **Regístrate** en la pantalla de
inicio de sesión; queda con el rol `paciente` en Keycloak.

---

## Dueños por Corte 1

| Integrante | HU | Backend | Frontend |
|---|---|---|---|
| Leyder Cerón | Agendamiento autónomo | `backend/app/modules/appointment/` (`scheduling/`, `validators/`, `builder/`) + `medical_staff/domain/factory/` | `frontend/src/app/features/appointments/agendamiento-autonomo/` |
| Andrea Gómez | Listar citas | `backend/app/modules/appointment/api/routes.py` (`listByDoctorAndDate`) | `frontend/src/app/features/appointments/listar-citas/` |
| Santiago Gutiérrez | Configuración del sistema | `backend/app/modules/configuration/` (+ apoyo en `medical_staff/`) | `frontend/src/app/features/configuration/` |

**Compartido** (acordar quién lo arranca primero): `backend/app/core/` (config, DB,
seguridad, event bus) y `frontend/src/app/core/` (interceptor JWT, guards) — las tres
features dependen de esto para poder probar contra el backend real.

---

## Backend (FastAPI)

```
backend/app/
├── main.py                 # crea la app y monta el router de cada módulo
├── core/                   # transversal: config, database (1 BD, schema por módulo),
│                           # security (valida los tokens de Keycloak y exige roles),
│                           # event_bus (in-process, reemplaza RabbitMQ), exceptions
├── modules/
│   ├── appointment/        # dominio ya migrado como referencia: entities, validators/
│   │                       # (Strategy/Chain), application/scheduling/ (Template Method:
│   │                       # base + manual + autonomous), infrastructure/repository.py
│   ├── configuration/      # esqueleto: entities, application/service.py, api/routes.py
│   ├── medical_staff/      # domain/factory/ (Factory Method: AvailabilityGenerator)
│   ├── patient/            # registro de pacientes (crea su cuenta a través de identity)
│   └── identity/           # inicio de sesión y cuentas de usuario sobre Keycloak
```

### Cómo correrlo

```bash
cd backend
python -m venv .venv && .venv/Scripts/activate   # Windows
pip install -r requirements.txt
python -m app.seed        # crea las tablas y carga datos de ejemplo (opcional)
uvicorn app.main:app --reload
```

`GET http://localhost:8000/health` debe responder `{"status": "ok"}`.
La documentación interactiva de la API queda en `http://localhost:8000/docs`.

Por defecto usa **SQLite** (`piedrazul.db`) para poder levantarlo sin instalar nada más.
Para usar PostgreSQL con un schema por módulo, crea un `.env` en `backend/`:

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/piedrazul
```

Las tablas y los schemas se crean solos al arrancar la aplicación.

Todas las rutas, salvo el inicio de sesión y el registro de pacientes, exigen un token de
Keycloak. Para correr el backend fuera de Docker, levanta solo Keycloak con
`docker compose up -d keycloak`; el backend lo busca por defecto en `http://localhost:8080`
(se cambia con la variable `KEYCLOAK_URL`).

### Tests

```bash
cd backend
pytest
```

Cubren las reglas del validador de conflictos, la configuración del sistema
(`tests/modules/configuration/`), el listado de citas (`tests/modules/appointment/`), la
validación de tokens y los permisos por rol (`tests/core/`), el adaptador de Keycloak y el
inicio de sesión (`tests/modules/identity/`), el registro de pacientes
(`tests/modules/patient/`), la cadena de validación y el agendamiento autónomo
(`tests/modules/appointment/`), la disponibilidad (`tests/modules/medical_staff/`) y los
festivos (`tests/shared/`). No necesitan Keycloak: usan tokens firmados con una llave de
prueba y un proveedor de identidad en memoria. Las del agendamiento fijan la fecha en el
lunes 9 de marzo de 2026 para que festivos y fines de semana sean predecibles.

### Agendamiento autónomo

El paciente agenda su propia cita en cuatro pasos: servicio, profesional, fecha y hora, y
confirmación. Antes de guardarla, el backend aplica en orden la cadena de validadores de
`appointment/domain/validators/`:

1. Datos coherentes, cita en el futuro y motivo de al menos 5 caracteres.
2. No es festivo en Colombia.
3. El paciente existe y el profesional existe y está activo.
4. El profesional pertenece a la especialidad del servicio.
5. El paciente no tiene otra cita activa (agendada o reagendada).
6. La fecha está dentro de la ventana de agendamiento configurada.
7. La hora coincide con una franja del horario configurado del profesional.
8. Los servicios especializados exigen una autorización médica vigente: el médico la
   otorga al atender una Consulta General, se usa una sola vez y caduca al mes.
9. Nadie más tiene esa franja (la restricción única de la base cubre las reservas simultáneas).

| Endpoint | Rol | Uso |
|---|---|---|
| `GET /api/v1/appointments/me/options` | Paciente | Servicios habilitados, autorización vigente y cita activa |
| `GET /api/v1/medical/doctors/available?specialty=` | Cualquiera | Profesionales de la especialidad con su próxima fecha libre |
| `GET /api/v1/medical/availability/calendar?doctor_id=` | Cualquiera | Días de la ventana con cupos libres |
| `GET /api/v1/medical/availability?doctor_id=&date=` | Cualquiera | Franjas del día, marcando las ocupadas |
| `POST /api/v1/appointments/autonomous` | Paciente | Agenda la cita; el paciente se toma del token |
| `GET /api/v1/appointments/me` | Paciente | Citas del paciente |
| `PATCH /api/v1/appointments/me/{id}/cancel` | Paciente | Cancela una cita propia |
| `PATCH /api/v1/appointments/{id}/attend` | Médico | Marca la cita como atendida y opcionalmente autoriza un servicio |

La fecha y la hora "actuales" se calculan en la zona horaria de Colombia (`TIMEZONE`, por
defecto `America/Bogota`), aunque el contenedor corra en UTC.

### Estado de los módulos

| Módulo | Estado |
|---|---|
| `appointment` | Listado por médico/fecha y por paciente, con filtros de servicio y estado. Agendamiento autónomo con cadena de validadores, Builder, autorización médica y cancelación por el paciente |
| `configuration` | Ventana de agendamiento y horario semanal por profesional |
| `medical_staff` | Registro de profesionales y cálculo de franjas, días disponibles y próxima fecha libre a partir del horario configurado |
| `patient` | Registro de pacientes con su cuenta de acceso (`POST /register`) y perfil propio (`GET /me`); expone un directorio consultado por el módulo de citas |
| `identity` | Inicio, renovación y cierre de sesión contra Keycloak (`/api/v1/auth`); crea las cuentas de los pacientes |

---

## Frontend (Angular 22, standalone components)

```
frontend/src/app/
├── core/                    # api-config.ts, auth/ (sesión y roles), interceptors/auth-interceptor.ts,
│                            # guards/auth-guards.ts
├── layout/shell/            # barra lateral según el rol del usuario
├── shared/                  # fechas en español, mensajes de error y diálogo de confirmación
└── features/
    ├── appointments/
    │   ├── listar-citas/            <- Andrea
    │   ├── agendamiento-autonomo/   <- Leyder
    │   ├── services/appointment.service.ts
    │   └── models/appointment.model.ts
    ├── configuration/
    │   ├── configuracion-global/       <- Santiago
    │   ├── configuracion-profesional/  <- Santiago
    │   └── services/configuration.service.ts
    ├── medical-staff/           # servicio de apoyo (médicos, disponibilidad)
    ├── patient/                 # inicio/ y mis-citas/ del paciente
    └── auth/                    # login/ (pestañas Paciente y Profesional) y registro/
```

### Cómo correrlo

> El workspace se generó con `--skip-install`, falta instalar dependencias.

```bash
cd frontend
npm install
npm start   # ng serve, http://localhost:4200
```

Las rutas están conectadas con lazy loading en `app.routes.ts`:

| Ruta | Acceso |
|---|---|
| `/login`, `/registro` | Sin sesión |
| `/appointments/listar` | Agendador, médico y administrador |
| `/paciente/inicio`, `/paciente/citas`, `/appointments/agendar` | Paciente |
| `/configuration`, `/configuration/global`, `/configuration/profesional` | Administrador |

Al iniciar sesión cada usuario llega a su pantalla principal según su rol.

---

## Decisión de base de datos

Una sola instancia **PostgreSQL**, con un schema por módulo (`appointment`,
`configuration`, `medical_staff`, ...) en vez de una BD física por módulo. Cada módulo
solo debe tocar su propio schema desde `infrastructure/`.

Los scripts `init-*.sql` en `../Mircoservicios/piedrazul/docker/postgres/` sirven de
base para los `CREATE TABLE` de cada schema — solo hay que adaptarlos.
