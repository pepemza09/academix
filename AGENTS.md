# Academix AI Development Instructions

Academix es una aplicación de gestión académica universitaria. Para las decisiones de **stack técnico** (Docker, PostgreSQL, Redis, Nginx/Gunicorn, React/Vite/TailAdmin) y de **UX/UI**, consulta `agents_base.md`. Este archivo documenta únicamente la **lógica de negocio** del dominio académico.

> La base técnica y de UI/UX es reutilizable: si quieres comenzar otro sistema con el mismo stack, centra tu trabajo en representar un dominio distinto siguiendo los patrones de negocio aquí documentados.

## Contexto que debe cargarse

- `agents_base.md` (stack + UX/UI + comandos + convenciones) antes de cualquier cambio.
- Los skills de `autoskills/packages/autoskills/skills-registry/*`: **bajarlas del repositorio** [`https://github.com/midudev/autoskills`](https://github.com/midudev/autoskills) (clon/pull, no están incluidas en el checkout por defecto) y **leerlas** antes de trabajar (ver listado en `agents_base.md`).

## Dominio académico (lógica de negocio)

El dominio es jerárquico y usa códigos únicos dentro de su nivel padre y estado activo/inactivo. En orden de dependencia:

### University (Universidad)
- Campos: `name`, `short_name` (abreviatura, ej. `UNCUYO`), `is_active`.
- Tiene N `AcademicUnit`.
- **No se puede eliminar** si tiene unidades académicas asociadas (400).

### AcademicUnit (Unidad académica)
- Pertenece a una `University`; código único dentro de la universidad, nombre corto, nombre completo, estado activo.
- Tiene sedes (`Campus`) y carreras (`Career`).
- **No se puede eliminar** si tiene sedes o carreras asociadas (400).

### Campus (Sede)
- Pertenece a una `AcademicUnit`; campos: `code`, `name`, `is_active`.

### Career (Carrera)
- Pertenece a una `AcademicUnit` (**la facultad es la `AcademicUnit`**).
- Multiselección de `Campus` (M2M): sedes donde se dicta.
- Campos: `code`, `short_name`, `name`, `is_active`.
- Tiene N `StudyPlan`.
- **No se puede eliminar** si tiene planes de estudio asociados (400).

### StudyPlan (Plan de estudio)
- Pertenece a una `Career`; una carrera puede tener uno o más planes.
- Campos: `code`, `title` (título que otorga), `intermediate_title` (título intermedio, opcional), `duration_years` (duración en años de la carrera, usado para validar el año de las materias), `is_active` (activo/inactivo), `is_current` (vigente/no vigente).
- Tiene N `StudyArea`.
- **No se puede eliminar** si tiene áreas asociadas (400).

### StudyArea (Área)
- Pertenece a un `StudyPlan`; campos: `name`, `is_active`.
- Tiene N `Subject`.
- **No se puede eliminar** si tiene materias asociadas (400).

### Subject (Materia)
- Pertenece a un `StudyArea`.
- Campos: `code` (código de la materia), `name` (nombre), `year` (año en el que se dicta; se valida contra `duration_years` del plan -> 1..duración), `period` (periodo de dictado, opciones fijas: 1er/2do cuatrimestre, 1er-4to bimestre, anual), `is_active`.
- El serializer expone además: `period_label`, `study_area_name`, `study_plan_code`, `study_plan_title`, `career_name`, `career_code`, `duration_years`.

## Endpoints API de negocio (bajo `/api/`)

| Recurso | Endpoint | Notas |
|---------|----------|-------|
| Universidad | `/api/universities/` | annotate `academic_unit_count` |
| Unidad académica | `/api/academic-units/` | expone `university` (editable), `university_name`, `campus_count` |
| Sede | `/api/campuses/` | expone `academic_unit` (editable), `academic_unit_name` |
| Carrera | `/api/careers/` | `academic_unit` (editable), `academic_unit_name`, `campuses` (editable), `campus_count`, `campus_details` (lectura: `[{id, code, name}]`) |
| Plan de estudio | `/api/study-plans/` | `career` (editable), `career_name`, `career_code`, `intermediate_title`, `duration_years`, `is_active`, `is_current` |
| Área | `/api/study-areas/` | `study_plan` (editable), `study_plan_code`, `study_plan_title`, `career_name`, `career_code`, `is_active` |
| Materia | `/api/subjects/` | `study_area` (editable), `study_area_name`, `study_plan_code/title`, `career_name/code`, `period` (editable) + `period_label`, `year` (validado contra `duration_years`), `duration_years`, `is_active` |

Protección de eliminación verificada (regla de integridad referencial):
- `DELETE /api/universities/{id}/` con unidades asociadas -> 400; sin unidades -> 204.
- `DELETE /api/academic-units/{id}/` con sedes o carreras asociadas -> 400; sin dependencias -> 204.
- `DELETE /api/campuses/{id}/` asociado a carreras (M2M `career.campuses`) -> 400; sin asociación -> 204.
- `DELETE /api/careers/{id}/` con planes asociados -> 400.
- `DELETE /api/study-plans/{id}/` con áreas asociadas -> 400.
- `DELETE /api/study-areas/{id}/` con materias asociadas -> 400; sin materias -> 204.

## Archivos clave de negocio

- `backend/config/urls.py`: serializers + viewsets de negocio y endpoints auth.
- `backend/apps/academics/models.py`: modelos `University`, `AcademicUnit`, `Campus`, `Career`, `StudyPlan`, `StudyArea`, `Subject`.
- `backend/apps/academics/migrations/0001_initial.py` ... `0007_studyplan_intermediate_title.py`, `0008_studyplan_duration_years_subject.py`.
- `backend/apps/academics/tests.py`: validación funcional de los modelos.
- `frontend/src/api/universities.ts`, `academicUnits.ts`, `campuses.ts`, `careers.ts`, `studyPlans.ts`, `studyAreas.ts`, `subjects.ts`: servicios API por entidad.
- `frontend/src/pages/Institucional/Universidad.tsx`: CRUD de universidades.
- `frontend/src/pages/Institucional/UnidadAcademica.tsx`: CRUD de unidades académicas con combobox de universidad.
- `frontend/src/pages/Institucional/Sede.tsx`: CRUD de sedes con combobox de unidad académica.
- `frontend/src/pages/Academica/Carreras.tsx`: CRUD de carreras (universidad → unidad académica + multiselección de sedes).
- `frontend/src/pages/Academica/Planes.tsx`: CRUD de planes de estudio (universidad → unidad académica → carrera), con duración en años.
- `frontend/src/pages/Academica/Areas.tsx`: CRUD de áreas (universidad → unidad académica → carrera → plan).
- `frontend/src/pages/Academica/Materias.tsx`: CRUD de materias (universidad → unidad académica → carrera → plan → área), con año y periodo.
- `frontend/src/pages/Dashboard/AcademicsHome.tsx`: resumen de solo lectura con métricas.

## Reglas de negocio de la UI (patrón por CRUD)

- **Selección jerárquica en cascada dentro del modal**: se elige primero la entidad raíz y cada nivel siguiente se filtra por la selección anterior (soporta varias universidades): universidad → unidad académica → carrera → plan.
- **Carreras**: checkboxes de sedes de la unidad académica seleccionada (multiselección). El listado muestra los códigos de las sedes.
- **Planes**: el formulario pide código del plan, título que otorga, duración en años (valida el año de las materias) y toggles "Activo" y "Vigente". El listado muestra código, título, duración, carrera (nombre + código), estado activo y vigente.
- **Áreas**: formulario con nombre del área y toggle "Activa". El listado muestra nombre, plan (título + código) y carrera (nombre + código).
- **Materias**: formulario con cascada universidad → unidad académica → carrera → plan → área, código de la materia, nombre, año de dictado (input numérico limitado a la duración del plan) y periodo (select con opciones fijas de cuatrimestres/bimestres/anual). El listado muestra código, nombre, año, periodo, área, plan, carrera y estado.
- Todas las páginas tienen búsqueda y filtro por estado activo.

## Handoff de desarrollo: estado actual del dominio

- CRUD funcional (frontend + backend) de: universidades, unidades académicas, sedes, carreras, planes de estudio, áreas y materias, conectados a la API bajo `/api/` con búsqueda y filtro por estado, con protección de eliminación por dependencias.
- Dashboard (`AcademicsHome.tsx`) es un resumen de solo lectura.
- Existe un superusuario local `admin` (creado previamente; sin commitear credenciales reales, están en `.env`).
- Backend: `manage.py check` OK y 31 tests pasan.
- CRUD validados de extremo a extremo (create 201, patch 200, list 200, delete 204) con sesión + CSRF.

### Optimización de rendimiento (frontend)

- **Code-splitting**: `App.tsx` carga todas las rutas con `React.lazy` + `Suspense`. El bundle principal bajó de 674KB a ~286KB (gzip ~90KB); cada página CRUD es un chunk separado (~12KB) y el Calendario (264KB) se carga on-demand.
- **Updates optimistas en las páginas CRUD**: al crear/editar/eliminar, las 6 páginas (`Universidad`, `UnidadAcademica`, `Sede`, `Carreras`, `Planes`, `Areas`) actualizan el estado local con la respuesta de la API en lugar de relanzar `fetchData()` (que recargaba todas las listas de dependencias por red). `fetchData()` solo corre en el `useEffect` inicial de montaje.
- **Backend `/api/auth/me/`**: `user_payload` usa una consulta read-only (`Profile.objects.filter(...).only("avatar")`) en vez de `get_or_create` por request; el perfil se crea solo al subir avatar.
- Los serializers de listado ya usan `select_related`/`prefetch_related`/`annotate` (sin N+1).

### Siguientes tareas recomendadas de negocio

1. **Verificar URIs de redirección de Google OAuth** en Google Cloud Console (ver `agents_base.md` para el callback).
2. **Expandir el dominio académico**: estudiantes, docentes, cursos, matrículas, periodos, notificaciones (siguiendo el patrón jerárquico con códigos + estado activo y protección de eliminación).
3. **Reforzar la capa de seguridad**: permisos, validación de CSRF, headers y manejo de sesiones en producción.
