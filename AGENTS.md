# Academix AI Development Instructions

Academix es una aplicación de gestión académica universitaria con un backend Django/DRF y un frontend React/Vite basado en TailAdmin. La arquitectura local se ejecuta con Docker Compose: Nginx, Gunicorn, Django, PostgreSQL y Redis.

## Contexto que debe cargarse

Antes de modificar código, el agente principal y cualquier subagente debe examinar:
- `autoskills/packages/autoskills/skills-registry/django-expert/SKILL.md`
- `autoskills/packages/autoskills/skills-registry/django-patterns/SKILL.md`
- `autoskills/packages/autoskills/skills-registry/django-security/SKILL.md`
- `autoskills/packages/autoskills/skills-registry/python-patterns/SKILL.md`
- `autoskills/packages/autoskills/skills-registry/python-testing-patterns/SKILL.md`
- `autoskills/packages/autoskills/skills-registry/redis-development/SKILL.md`
- el template TailAdmin en `template/` y el frontend activo en `frontend/`.

## Seguridad de configuración

Todas las claves, usuarios, tokens, contraseñas, OAuth credentials, URLs de conexión y demás valores sensibles deben centralizarse en `.env`. `.env` está ignorado por Git; solo `.env.example` se versiona con placeholders. Nunca imprimir, hardcodear o comitear secretos.

## Coordinación

- `academix-backend`: modelos, migraciones, API, permisos, autenticación y tests Django.
- `academix-frontend`: UI/UX, rutas, componentes TailAdmin, integración API y accesibilidad.
- El agente principal coordina contratos entre ambos: API bajo `/api/`, autenticación por sesión y Google OAuth bajo `/auth/`.
- Antes de una edición, formular una hipótesis local y una comprobación barata.
- Tras editar, ejecutar una validación enfocada; al finalizar ejecutar los tests o builds disponibles.

## Comandos principales

```bash
cp .env.example .env
python3 backend/manage.py check
python3 backend/manage.py test
cd frontend && npm ci && npm run build
docker compose up --build
```

## Dominio inicial

Existe una `University` (con `name`, `short_name`/abreviatura e `is_active`) y N `AcademicUnit`. Cada unidad posee código único dentro de la universidad, nombre corto, nombre completo y estado activo.

## Handoff de desarrollo: estado actual y contexto operativo

Este archivo sirve como contexto de continuidad para el siguiente agente IA. Debe leerse antes de comenzar un cambio funcional.

### Estado verificado del proyecto

- La aplicación está diseñada como una plataforma académica universitaria con backend Django/DRF y frontend React/Vite con TailAdmin.
- La infraestructura local corre en Docker Compose con servicios principales: `backend`, `frontend`, `db`, `redis` y `nginx`.
- El backend se ejecuta con Gunicorn, el frontend se sirve por Nginx y la base de datos es PostgreSQL 16.10 Alpine.
- Las credenciales, URLs, OAuth, secretos y configuración sensible viven en `.env`; `.env.example` es la plantilla versionada.
- El proyecto ya está funcionalmente levantado y verificado en su estado actual.

### Problemas resueltos y decisiones ya tomadas

1. PostgreSQL / volumen incompatibles
   - El proyecto había sido inicializado con PostgreSQL 17, pero el volumen local ya estaba creado con una versión anterior.
   - Se corrigió el compose para usar `postgres:16.10-alpine` y se evitó destruir datos previos de forma agresiva.
   - El resultado es que la base de datos ya arranca correctamente y los servicios siguen saludables.

2. Nginx y headers del host
   - El backend rechazaba solicitudes con `HTTP_HOST=academix_backend` o un host externo no consistente.
   - Se ajustó la config del proxy inverso para conservar el host público y evitar errores de host/CSRF o errores de proxy.
   - El backend responde correctamente a través de Nginx.

3. Estado de servicios y arranque
   - Hubo un problema inicial con 502 durante arranque porque Gunicorn no estaba listo aún.
   - Se solucionó con reinicios y validación posterior del estado real del servicio.
   - El stack queda en estado operativo y se recomienda validar con `docker compose ps` antes de tratar fallos de red.

4. Frontend desactualizado / caché visual
   - El contenedor del frontend entregaba una versión anterior del build.
   - Se reconstruyó el frontend y se reinició Nginx.
   - Si el navegador sigue mostrando contenido viejo, debe forzarse recarga con `Ctrl + F5`.

5. Branding visual de Academix
   - El nombre visible del producto estaba incorrecto en algunos assets y se mostraba `LINEX` en lugar de `Academix`.
   - Se actualizó el SVG del logo, el favicon y el título de la pestaña para usar la marca correcta.
   - El color principal se mantiene en la paleta TailAdmin con `#465FFF`.
   - El texto visible en el logo ahora debe ser `Academix` y el color del símbolo/texto correcto.

6. CRUD de universidades completo (frontend + backend)
   - El modelo `University` ahora tiene `short_name` (abreviatura, ej. `UNCUYO`) e `is_active` (migración `0002` aplicada).
   - Endpoint `/api/universities/` (UniversityViewSet con `IsAuthenticated`) para listar, crear, editar (PATCH) y eliminar.
   - Página `frontend/src/pages/Institucional/Universidad.tsx` con CRUD completo conectado a la API.
   - Se eliminó el bloque de texto "Institucional / Universidades / Administra..." por redundante; el botón "Nueva universidad" quedó sin ícono y en negrita.
   - Las tarjetas de métricas de la página se eliminaron; muestra solo el listado.
   - Estado "activa" del modal se maneja con un componente `Switch` (toggle).
   - Ambos modales (alta/edición y eliminación) quedaron centrados; el de eliminación ocupa como máximo el 40% de la pantalla y mantiene el blur de fondo (prop `centered` agregada al `Modal`).

7. Autenticación en el frontend (login local + Google OAuth)
   - Se creó `frontend/src/context/AuthContext.tsx` (AuthProvider) que carga la sesión vía `GET /api/auth/me/` y expone `user`, `login`, `loginWithGoogle` y `logout`.
   - `frontend/src/api/auth.ts`: servicio con `me`, `login`, `logout` y `GOOGLE_LOGIN_URL`.
   - `SignInForm.tsx` conectado: login local (usuario/contraseña) y botón "Sign in with Google".
   - `ProtectedRoute` (`frontend/src/components/common/ProtectedRoute.tsx`) protege el layout autenticado y redirige a `/signin`.
   - `UserDropdown.tsx` muestra el usuario real y botón "Sign out" que llama a `logout`.
   - En el backend, `login_view`, `me` y `logout_view` usan `@ensure_csrf_cookie` para emitir la cookie CSRF al navegador.

8. Zoom persistido por usuario
   - El nivel de zoom se guarda en `localStorage` (clave `zoom`) en `frontend/src/context/ThemeContext.tsx`; se inicializa de forma síncrona al montar.

9. Menú del sidebar reorganizado
   - `AppSidebar.tsx`: "Dashboard" quedó como enlace directo (sin submenú) y se agregó el menú "Institucional" con los submenús Universidad, Unidad Académica y Sede.
   - Se eliminó `SidebarWidget.tsx` (bloque "Academix académico / Ir al resumen").
   - La sidebar usa `inset-y-0` en lugar de `h-screen` para cubrir el alto visible en cualquier nivel de zoom.

10. Volumen de desarrollo del frontend
    - Se agregó bind-mount `./frontend:/app` (+ ancla `/app/node_modules`) al servicio `frontend` para que Vite refleje los cambios sin reconstruir la imagen.

### Archivos clave del proyecto

- `docker-compose.yml`: orquestación principal del entorno local.
- `backend/config/settings.py`: configuración global de Django, seguridad y entorno.
- `backend/config/urls.py`: endpoints API, health, auth y viewsets (University, AcademicUnit, Campus, Career).
- `backend/apps/academics/models.py`: dominio de `University`, `AcademicUnit`, `Campus` y `Career`.
- `backend/apps/academics/migrations/0001_initial.py`, `0002_*`, `0003_campus` y `0004_career`: migraciones aplicadas.
- `backend/apps/academics/tests.py`: validación funcional de los modelos.
- `frontend/src/api/client.ts`: cliente fetch con cookies, CSRF y manejo de errores.
- `frontend/src/api/auth.ts`, `universities.ts`, `academicUnits.ts`, `campuses.ts`, `careers.ts`: servicios API.
- `frontend/src/components/form/Combobox.tsx`: componente reutilizable de selección con búsqueda (input + lista desplegable filtrable).
- `frontend/src/context/AuthContext.tsx`: estado de sesión, login, logout y Google.
- `frontend/src/context/ThemeContext.tsx`: tema dark/light y zoom persistido.
- `frontend/src/components/common/ProtectedRoute.tsx`: protección de rutas autenticadas.
- `frontend/src/components/ui/modal/index.tsx`: Modal con props `centered`/`isFullscreen`.
- `frontend/src/pages/Dashboard/AcademicsHome.tsx`: resumen general con métricas y listado de solo lectura de unidades académicas.
- `frontend/src/pages/Institucional/Universidad.tsx`: CRUD de universidades.
- `frontend/src/pages/Institucional/UnidadAcademica.tsx`: CRUD de unidades académicas con combobox de universidad.
- `frontend/src/pages/Institucional/Sede.tsx`: CRUD de sedes con combobox de unidad académica.
- `frontend/src/pages/Academica/Carreras.tsx`: CRUD de carreras (facultad + multiselección de sedes) y `frontend/src/pages/Academica/Planes.tsx`: placeholder.
- `frontend/src/layout/AppSidebar.tsx`: navegación principal (Dashboard + Institucional + Académica).
- `frontend/index.html`: favicon y título de la pestaña.
- `frontend/public/images/logo/*.svg`: assets del logo actualizados.
- `.env` y `.env.example`: secretos y configuración centralizada.

### Validaciones ejecutadas y confirmadas

Se han verificado los siguientes puntos con evidencia real:

- `python3 backend/manage.py check` -> OK.
- `python3 backend/manage.py test` -> 8 tests pasados.
- `cd frontend && npm run build` -> build correcto con warnings existentes no bloqueantes.
- `docker compose ps --format 'table {{.Service}}\t{{.Status}}'` -> servicios activos.
- `curl -fsS http://localhost/images/logo/academix-logo.svg | grep -E '465FFF|Academix'` -> asset público con texto y color correctos.
- CRUD `/api/universities/`, `/api/academic-units/`, `/api/campuses/` y `/api/careers/` validados de extremo a extremo (create 201, patch 200, list 200, delete 204) con sesión + CSRF.
- Protección verificada: `DELETE /api/universities/{id}/` con unidades asociadas -> 400; sin unidades -> 204. `DELETE /api/academic-units/{id}/` con sedes o carreras asociadas -> 400; sin dependencias -> 204.

### Estado funcional actual

- La infraestructura base está operativa.
- Django está configurado y pasa la validación.
- La base de datos y Redis están disponibles.
- El frontend está construido y sirve la marca correcta.
- Login local (usuario/contraseña) funciona de extremo a extremo con sesión + CSRF.
- Google OAuth configurado con credenciales reales en `.env` local (no versionadas).
  - `LOGIN_REDIRECT_URL = "/"` -> tras autenticar vuelve al dashboard SPA y el frontend recupera la sesión vía `me()`.
  - Callback: `http://localhost/auth/complete/google-oauth2/` (debe registrarse como Authorized redirect URI en Google Cloud Console).
- CRUD de universidades funcional (frontend + backend) con `short_name` e `is_active`.
  - `UniversityViewSet.destroy` bloqueado (400) si la universidad tiene unidades académicas asociadas.
- CRUD de unidades académicas funcional en `frontend/src/pages/Institucional/UnidadAcademica.tsx` con selector de universidad (combobox con búsqueda), código, nombre corto, nombre completo, toggle de estado y protección de eliminación.
  - Backend: `AcademicUnitSerializer` expone `university` (editable), `university_name` (lectura) y `campus_count`.
  - `AcademicUnitViewSet.destroy` bloqueado (400) si tiene sedes o carreras asociadas.
- CRUD de sedes funcional en `frontend/src/pages/Institucional/Sede.tsx` con combobox de unidad académica (búsqueda), código, nombre, toggle de estado y búsqueda/filtro en el listado.
  - Backend: modelo `Campus` (FK a `AcademicUnit`), `CampusViewSet` en `/api/campuses/`, serializer con `academic_unit` (editable) y `academic_unit_name` (lectura).
- CRUD de carreras funcional en `frontend/src/pages/Academica/Carreras.tsx` (módulo Académica del sidebar).
  - La **facultad** es la `AcademicUnit`: cada carrera pertenece a una unidad académica.
  - Backend: modelo `Career` (FK `academic_unit` = facultad, M2M `campuses` = sedes donde se dicta, `code`, `short_name`, `name`, `is_active`), migración `0004_career`, `CareerViewSet` en `/api/careers/` (prefetch campuses, `select_related` académica, annotate `campus_count`), serializer expone `academic_unit` (editable), `academic_unit_name` (lectura), `campuses` (editable), `campus_count` (lectura) y `campus_details` (lectura: `[{id, code, name}]` de las sedes).
  - Frontend: en el modal se elige primero **universidad** y las **facultades (unidades académicas)** y **sedes** se filtran por esa universidad (soporta varias universidades); checkboxes de sedes de la facultad seleccionada (multiselección), código, nombre corto, nombre, toggle "Carrera activa", búsqueda y filtro de estado. El listado muestra los **códigos** de las sedes de cada carrera. Planes es placeholder: `Planes.tsx`.
- Dashboard (`AcademicsHome.tsx`) muestra "Resumen general" con métricas y listado de solo lectura de unidades (el CRUD vive en la página Institucional/UnidadAcademica).
- Existe un superusuario local `admin` (creado en estas tareas; sin commitear credenciales reales).

### Siguientes tareas recomendadas

1. Registrar/verificar URIs de redirección en Google Cloud Console
   - Confirmar que `http://localhost/auth/complete/google-oauth2/` esté en Authorized redirect URIs de la OAuth Client.
   - Probar el flujo completo en el navegador (botón "Sign in with Google" -> volver al dashboard).

2. Expandir el dominio académico
   - Añadir más modelos y endpoints según el backlog: planes de estudio (el CRUD de carreras ya marca la base), estudiantes, docentes, cursos, matrículas, periodos, notificaciones.

3. Reforzar la capa de seguridad
   - Revisar permisos, validación de CSRF, headers y manejo de sesiones en producción.

### Reglas de continuación

- No hardcodear secretos ni valores sensibles en código.
- Mantener `.env` fuera del control de versiones; solo `.env.example` debe versionarse.
- Antes de editar, formular una hipótesis simple y ejecutar una validación breve.
- Tras cambios, ejecutar al menos: validación del backend (`manage.py check` o tests) o build del frontend si se modifica UI.
- Si se trabaja con Docker, validar el estado real con `docker compose ps` y reintentar con `docker compose up -d --build <servicio>` cuando sea requerido.
- Si la marca visual parece no actualizarse, evitar repetir cambios hasta forzar caché del navegador (`Ctrl + F5`).
- El servicio `frontend` monta `./frontend:/app` (bind-mount), por lo que los cambios se reflejan sin reconstruir la imagen; tras editar JS/TSX conviene validar con el build.
- El backend monta `./backend:/app`; Gunicorn no hace hot-reload, por lo que tras editar backend hay que reconstruir/reiniciar el servicio.

### Comandos de referencia

```bash
cp .env.example .env
python3 backend/manage.py check
python3 backend/manage.py test
docker compose ps --format 'table {{.Service}}\t{{.Status}}'
cd frontend && npm run build
docker compose up -d --build frontend
docker compose restart nginx
```

### Resumen ejecutivo

La base del proyecto está preparada, dockerizada y validada con branding de Academix corregido. Ya están funcionales: autenticación local, Google OAuth (credenciales reales en `.env`, `LOGIN_REDIRECT_URL="/"`, callback `/auth/complete/google-oauth2/`), protección de rutas, zoom y tema persistidos, CRUD de universidades, CRUD de unidades académicas, CRUD de sedes y CRUD de carreras (módulo Académica, con la unidad académica como facultad y multiselección de sedes), todos conectados a la API bajo `/api/` con búsqueda y filtro por estado. El dashboard es un resumen de solo lectura. Queda pendiente: verificar las URIs de redirección de Google Cloud Console y la expansión del dominio académico. El siguiente agente debe centrarse en la expansión del dominio, manteniendo la seguridad y la estructura ya validada.
