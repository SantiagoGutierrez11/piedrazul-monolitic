# E7-HU1 · Historial de citas de un paciente por cédula

> **Yo como** médico/terapista/agendador **necesito** consultar las citas de un paciente a partir
> de su cédula **para** conocer el historial de citas que ha tenido.

Pantalla: **Historial de Paciente** (`/appointments/historial`), en la barra lateral del médico,
del agendador y del administrador.

## Reglas definidas

### 2.1 · Formato de la cédula y autocompletado

| Regla | Valor |
|---|---|
| Caracteres permitidos | Solo dígitos: sin puntos, letras, espacios ni guiones |
| Longitud | De 5 a 10 dígitos (el registro de pacientes acepta documentos desde 5 caracteres) |
| Autocompletado | Se activa desde el **3.er dígito** y sugiere pacientes cuya cédula **empieza** por lo escrito |
| Sugerencias | Máximo 8; cada una muestra el nombre, el tipo de documento y la cédula con lo escrito resaltado |
| Búsqueda exacta (botón **Buscar** o Enter) | Pide la cédula completa (5 a 10 dígitos) |

Mensajes de formato:

- *"La cédula solo puede tener números, sin puntos, letras ni espacios."*
- *"La cédula tiene como máximo 10 dígitos."*
- *"Escribe la cédula completa: tiene al menos 5 dígitos."*

### 2.2 · Orden y datos del historial

- **Orden:** de la cita más reciente a la más antigua; si hay dos el mismo día, primero la de
  hora más tarde.
- **Columnas:** Fecha, Hora, Profesional, Servicio y Estado.
- **Alcance:** el historial es completo. Incluye las citas futuras (agendadas o reagendadas), las
  atendidas y las canceladas, con todos los profesionales.
- **Datos del paciente:** nombre, tipo y número de documento, teléfono y total de citas. No se
  muestran correo, dirección ni otros datos personales.

### 2.3 · Roles

| Rol | ¿Consulta el historial por cédula? |
|---|---|
| Médico / terapista (`medico`) | ✅ Sí |
| Agendador (`agendador`) | ✅ Sí |
| Administrador (`administrador`) | ✅ Sí. No aparece en la historia de usuario, pero el equipo decidió incluirlo porque supervisa el centro |
| Paciente (`paciente`) | ❌ No. Ve solo sus propias citas en **Mis citas** |

El backend rechaza con **403** a cualquier otro rol, aunque llame directamente a la API.

## 2.4 · Criterios de aceptación

**Escenario 1: Buscar una cédula existente y ver su historial completo**
- **Dado** que soy médico, agendador o administrador y María García López (CC 1061234567) tiene citas registradas
- **Cuando** escribo `106123` en el campo de cédula y elijo a María en la lista de sugerencias
- **Entonces** veo su nombre, su cédula, su teléfono y el total de citas
- **Y** veo todas sus citas (incluidas las canceladas) con fecha, hora, profesional, servicio y
  estado, de la más reciente a la más antigua

**Escenario 2: Cédula que no existe**
- **Dado** que soy médico, agendador o administrador
- **Cuando** escribo una cédula válida que no pertenece a ningún paciente y pulso **Buscar**
- **Entonces** veo el mensaje *"Paciente no encontrado"*
- **Y** no se muestra ninguna tabla de historial

**Escenario 3: Paciente registrado sin citas**
- **Dado** que Camila Rojas (CC 1066789012) está registrada pero no tiene citas
- **Cuando** busco su cédula
- **Entonces** veo su ficha con *"0 citas registradas"*
- **Y** el mensaje *"Sin citas registradas"* en lugar de la tabla

**Escenario 4: Cédula con formato inválido**
- **Dado** que soy médico, agendador o administrador
- **Cuando** escribo una cédula con letras, puntos o espacios (por ejemplo `1.061.234.567`)
- **Entonces** el campo se marca en rojo con el mensaje *"La cédula solo puede tener números, sin
  puntos, letras ni espacios."*
- **Y** no se muestran sugerencias ni se hace la búsqueda

**Escenario 5: Un paciente no puede consultar el historial de otro**
- **Dado** que inicié sesión como paciente
- **Cuando** intento abrir la pantalla de historial o llamar a la API del historial de otro paciente
- **Entonces** la aplicación no me muestra la opción en la barra lateral y me devuelve a mi inicio
- **Y** la API responde **403** *"No tienes permiso para consultar el historial de citas de un
  paciente"*

## Dónde están las reglas en el código

| Regla | Backend | Frontend |
|---|---|---|
| 2.1 Formato y autocompletado | `backend/app/modules/patient/application/document_search.py` | `historial-paciente.reglas.ts` |
| 2.2 Orden y columnas | `backend/app/modules/appointment/application/patient_history.py` | `historial-paciente.reglas.ts` |
| 2.3 Roles | `patient_history.py` (`HISTORY_ROLES`) | `historial-paciente.reglas.ts` (`ROLES_HISTORIAL`) |
