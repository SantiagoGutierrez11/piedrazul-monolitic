# E7-HU1 · Casos de prueba del historial por cédula

Casos de prueba de la historia **"Yo como médico/terapista/agendador necesito consultar las citas
de un paciente a partir de su cédula para conocer el historial de citas que ha tenido"**. Cada caso
corresponde a un escenario de los criterios de aceptación
([E7-HU1-historial-por-cedula.md](E7-HU1-historial-por-cedula.md)).

## Preparación

1. Levanta la aplicación y carga los datos de ejemplo:

   ```bash
   docker compose up --build -d
   docker compose exec backend python -m app.seed
   ```

2. Abre http://localhost:4200 e inicia sesión con el usuario que indique cada caso.

| Usuario | Correo | Contraseña |
|---|---|---|
| Médico | `medico@piedrazul.com` | `medico123` |
| Agendador | `agendador@piedrazul.com` | `agendador123` |
| Administrador | `admin@piedrazul.com` | `admin123` |
| Paciente (María García López) | `paciente@piedrazul.com` | `paciente123` |

| Paciente de ejemplo | Cédula | Citas |
|---|---|---|
| María García López | 1061234567 | Tiene citas (agendadas, atendidas y canceladas) |
| Carlos Rodríguez | 1061234890 | Tiene citas |
| Camila Rojas | 1066789012 | **Ninguna** |

---

## 4.1 · Buscar una cédula existente y ver su historial completo

| | |
|---|---|
| **Escenario** | 1 de los criterios de aceptación |
| **Usuario** | Agendador (repetir con médico y administrador) |
| **Datos** | `106123` y luego María García López |

| # | Paso | Resultado esperado |
|---|---|---|
| 1 | Abrir **Historial de Paciente** en la barra lateral | Se ve el campo "Número de cédula" y el mensaje *"Escribe la cédula del paciente…"* |
| 2 | Escribir `10` | No aparecen sugerencias; la ayuda dice *"Escribe al menos 3 dígitos para ver sugerencias."* |
| 3 | Completar hasta `106123` | Aparece la lista con **María García López** y **Carlos Rodríguez**, con `106123` resaltado en azul |
| 4 | Bajar con **↓** y pulsar **Enter** (o hacer clic en María) | Aparece la ficha: nombre, `CC 1061234567`, teléfono y total de citas |
| 5 | Revisar la tabla | Columnas **Fecha, Hora, Profesional, Servicio, Estado**; están todas las citas, también las **canceladas**, de la **más reciente a la más antigua** |
| 6 | Pulsar **Limpiar**, escribir `1061234567` y pulsar **Buscar** | Se abre directamente el historial de María |

**Pruebas automáticas que lo cubren**
- Backend: `test_patient_search_api.py` → `test_suggests_patients_whose_id_number_starts_with_the_typed_digits`, `test_the_exact_match_comes_first`; `test_patient_history_api.py` → `test_staff_see_the_whole_history_from_the_newest_appointment` (médico, agendador y administrador)
- Frontend: `historial-paciente.spec.ts` → *asks the backend for suggestions from the third digit on*, *picks a suggestion with the keyboard and shows the history from the backend*, *finds the exact id number with the Buscar button*

---

## 4.2 · Cédula que no existe

| | |
|---|---|
| **Escenario** | 2 |
| **Usuario** | Médico |
| **Datos** | `999999` |

| # | Paso | Resultado esperado |
|---|---|---|
| 1 | Escribir `999999` | La lista dice *"Ningún paciente tiene una cédula que empiece por 999999."* |
| 2 | Pulsar **Buscar** | Aparece **"Paciente no encontrado"**: *"No encontramos un paciente registrado con la cédula 999999. Revisa el número e intenta de nuevo."* |
| 3 | Revisar la pantalla | No hay ficha ni tabla de historial |

**Pruebas automáticas**
- Backend: `test_patient_search_api.py` → `test_an_unknown_id_number_returns_an_empty_list`; `test_patient_history_api.py` → `test_an_unknown_patient_is_not_found`
- Frontend: `historial-paciente.spec.ts` → *tells the user when no patient has that id number*

---

## 4.3 · Paciente registrado sin citas

| | |
|---|---|
| **Escenario** | 3 |
| **Usuario** | Agendador |
| **Datos** | `1066789012` (Camila Rojas) |

| # | Paso | Resultado esperado |
|---|---|---|
| 1 | Escribir `1066789012` y pulsar **Buscar** | Aparece la ficha de **Camila Rojas** con **0 citas registradas** |
| 2 | Revisar debajo de la ficha | Mensaje **"Sin citas registradas"**: *"Camila Rojas no tiene citas registradas en Piedrazul."* No hay tabla |

**Pruebas automáticas**
- Backend: `test_patient_history_api.py` → `test_a_registered_patient_without_appointments_has_an_empty_history`
- Frontend: `historial-paciente.spec.ts` → *tells the user when the patient has no appointments yet*

---

## 4.4 · Cédula con formato inválido (letras o puntos)

| | |
|---|---|
| **Escenario** | 4 |
| **Usuario** | Administrador |
| **Datos** | `1.061.234.567`, `10612a`, `106 123`, `10612345678`, `1061` |

| # | Paso | Resultado esperado |
|---|---|---|
| 1 | Escribir `1.061.234.567` | El campo se pone **rojo** con *"La cédula solo puede tener números, sin puntos, letras ni espacios."*; no aparecen sugerencias |
| 2 | Pulsar **Buscar** | No se busca nada; sigue el mismo mensaje |
| 3 | Repetir con `10612a` y con `106 123` | Mismo mensaje |
| 4 | Escribir `10612345678` (11 dígitos) | *"La cédula tiene como máximo 10 dígitos."* |
| 5 | Escribir `1061` y pulsar **Buscar** | *"Escribe la cédula completa: tiene al menos 5 dígitos."* |

**Pruebas automáticas**
- Backend: `test_document_search.py` (todas); `test_patient_search_api.py` → `test_rejects_an_invalid_id_number` (la API responde **400** aunque se llame directamente)
- Frontend: `historial-paciente.reglas.spec.ts` → *accepts only digits, up to ten*, *needs at least five digits to search an exact id number*; `historial-paciente.spec.ts` → *rejects an id number with dots or letters without calling the backend*

---

## 4.5 · Un paciente no puede consultar el historial de otro

| | |
|---|---|
| **Escenario** | 5 |
| **Usuario** | Paciente (María) |
| **Datos** | Historial de Carlos Rodríguez (paciente 2) |

| # | Paso | Resultado esperado |
|---|---|---|
| 1 | Entrar como paciente y revisar la barra lateral | **No** aparece "Historial de Paciente" |
| 2 | Escribir en la barra de direcciones `http://localhost:4200/appointments/historial` | La aplicación lo devuelve a **su inicio** (`/paciente/inicio`) |
| 3 | (Opcional, con la API) Pedir `GET /api/v1/appointments/patient/2/history` con el token del paciente | **403** *"No tienes permiso para realizar esta operación"* |
| 4 | (Opcional, con la API) Pedir `GET /api/v1/patients/search?document=106123` con el token del paciente | **403**: el paciente tampoco puede buscar a otros pacientes |

**Pruebas automáticas**
- Backend: `test_patient_history_api.py` → `test_a_patient_cannot_see_the_history_of_another_patient`; `test_patient_search_api.py` → `test_patients_cannot_search_other_patients`; `test_patient_history_rules.py` → `test_a_patient_cannot_consult_the_history_of_others`
- Frontend: `appointments.routes.spec.ts` → *sends a patient back to their own home page*; `shell.spec.ts` → *shows only the patient options to a patient*

---

## Registro de ejecución

| Caso | Fecha | Usuario | Resultado obtenido | ¿Pasó? |
|---|---|---|---|---|
| 4.1 | | | | ☐ |
| 4.2 | | | | ☐ |
| 4.3 | | | | ☐ |
| 4.4 | | | | ☐ |
| 4.5 | | | | ☐ |

Pruebas automáticas (desde la raíz del proyecto, en PowerShell):

```powershell
# Backend: usa la imagen de Docker del backend con la carpeta tests/ montada
docker run --rm -v "${PWD}\backend:/src" -w /src piedrazul-monolitic-backend python -m pytest -q -p no:cacheprovider

# Frontend
cd frontend
npx ng test --watch=false
```

Si los tests del frontend fallan con *"Cannot find module …/rxjs…"*, es por el `#` del nombre de
la carpeta del proyecto (por ejemplo `Semestre##7`): Vitest no resuelve rutas con `#`. Ejecútalos
desde una unidad temporal sin `#`:

```powershell
subst P: "<ruta completa del proyecto>"
cd P:\frontend
npx ng test --watch=false
subst P: /D
```
