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

La forma más rápida de levantar todo (PostgreSQL + backend + frontend) sin instalar
Python ni Node:

```bash
docker compose up --build
```

| Servicio | URL |
|---|---|
| Frontend (Angular + nginx) | http://localhost:4200 |
| Backend (FastAPI) | http://localhost:8000 · docs en `/docs` |
| PostgreSQL | localhost:5432 (usuario/clave `postgres`) |

Los schemas y tablas de cada módulo se crean solos al arrancar el backend. Para cargar
datos de ejemplo y poder ver el listado de citas:

```bash
docker compose exec backend python -m app.seed
```

Para bajar todo (agrega `-v` si además quieres borrar la base de datos):

```bash
docker compose down
```

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
│                           # security (JWT — placeholder hasta Corte 2), event_bus (in-process,
│                           # reemplaza RabbitMQ), exceptions
├── modules/
│   ├── appointment/        # dominio ya migrado como referencia: entities, validators/
│   │                       # (Strategy/Chain), application/scheduling/ (Template Method:
│   │                       # base + manual + autonomous), infrastructure/repository.py
│   ├── configuration/      # esqueleto: entities, application/service.py, api/routes.py
│   ├── medical_staff/      # domain/factory/ (Factory Method: AvailabilityGenerator)
│   ├── patient/            # esqueleto mínimo
│   └── identity/           # esqueleto mínimo (Keycloak/JWT llega en el Corte 2)
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

### Tests

```bash
cd backend
pytest
```

Cubren las reglas del validador de conflictos, la configuración del sistema
(`tests/modules/configuration/`) y el listado de citas (`tests/modules/appointment/`).

### Estado de los módulos

| Módulo | Estado |
|---|---|
| `appointment` | Listado por médico/fecha y por paciente, con filtros de servicio y estado. Agendamiento autónomo (`POST /autonomous`) con cadena de validadores |
| `configuration` | Ventana de agendamiento y horario semanal por profesional |
| `medical_staff` | Registro de profesionales y cálculo de horarios disponibles |
| `patient` | Registro de pacientes; expone un directorio consultado por el módulo de citas |
| `identity` | Esqueleto: la autenticación real llega con Keycloak |

---

## Frontend (Angular 22, standalone components)

```
frontend/src/app/
├── core/                    # api-config.ts, interceptors/auth-interceptor.ts, guards/role-guard.ts
├── shared/                  # (vacío a propósito — mover aquí lo que se repita entre features)
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
    └── auth/login/              # placeholder mínimo, sin Keycloak todavía
```

### Cómo correrlo

> El workspace se generó con `--skip-install`, falta instalar dependencias.

```bash
cd frontend
npm install
npm start   # ng serve, http://localhost:4200
```

Las rutas ya están conectadas con lazy loading en `app.routes.ts`:

- `/login`
- `/appointments/listar`
- `/appointments/agendar`
- `/configuration/global`
- `/configuration/profesional`

---

## Decisión de base de datos

Una sola instancia **PostgreSQL**, con un schema por módulo (`appointment`,
`configuration`, `medical_staff`, ...) en vez de una BD física por módulo. Cada módulo
solo debe tocar su propio schema desde `infrastructure/`.

Los scripts `init-*.sql` en `../Mircoservicios/piedrazul/docker/postgres/` sirven de
base para los `CREATE TABLE` de cada schema — solo hay que adaptarlos.
