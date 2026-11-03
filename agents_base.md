# Academix — Base técnica: Stack y UX/UI

Este archivo documenta las decisiones relativas al **stack técnico** (infraestructura, arquitectura base, convenciones de desarrollo) y a la **UX/UI**. No contiene lógica de negocio específica; sirve como punto de partida reutilizable para comenzar otro sistema representando un dominio distinto.

## Arquitectura general

- **Backend**: Django / Django REST Framework (DRF).
- **Frontend**: React + Vite sobre el template **TailAdmin** (Tailwind CSS).
- **Infraestructura local**: Docker Compose con servicios `backend`, `frontend`, `frontend-dev` (perfil `dev`), `db`, `redis` y `nginx`. Todos los servicios corren con `security_opt: no-new-privileges:true`; el backend corre **sin root** (`user: 1000:1000`, uid alineado con el dueño del bind-mount, `HOME=/tmp` para el control socket de Gunicorn 26) y **solo `nginx` publica puertos** (80) — backend, db y redis no exponen puertos al host.
- **Servidores**: backend servido por Gunicorn; frontend servido por Nginx (proxy inverso). En la configuración por defecto el servicio `frontend` es una imagen multi-stage (build de Vite + `nginx:1.30.6-alpine` estático) y el proxy `/` apunta a ese estático; para desarrollo con hot-reload usar `docker compose --profile dev up` (levanta `frontend-dev`, Vite en :5173). El SPA consume `/api` **relativo** (`client.ts` hace fallback a `"/api"`), así que el build de producción no necesita envs horneados.
- **Base de datos**: PostgreSQL 16.10 Alpine.
- **Caché**: Redis con AUTH (password en `REDIS_PASSWORD`, conectado vía `REDIS_URL=redis://:<pw>@redis:6379/0`; healthcheck autenticado).
- **Estáticos de Django/panel admin con `DEBUG=false`**: `whitenoise==6.12.0` (middleware + `CompressedStaticFilesStorage`); el comando de arranque del backend corre `collectstatic` antes de Gunicorn.

## Contexto que debe cargarse antes de modificar código

El agente principal y cualquier subagente debe **bajar del repositorio** [`https://github.com/midudev/autoskills`](https://github.com/midudev/autoskills) (clon `git clone https://github.com/midudev/autoskills` o `git pull` para actualizar) y **leer** las skills antes de modificar código. El contenido se aloja localmente en `autoskills/` (por lo que `autoskills/` está excluido del checkout por defecto y de Git):
- `autoskills/packages/autoskills/skills-registry/django-expert/SKILL.md`
- `autoskills/packages/autoskills/skills-registry/django-patterns/SKILL.md`
- `autoskills/packages/autoskills/skills-registry/django-security/SKILL.md`
- `autoskills/packages/autoskills/skills-registry/python-patterns/SKILL.md`
- `autoskills/packages/autoskills/skills-registry/python-testing-patterns/SKILL.md`
- `autoskills/packages/autoskills/skills-registry/redis-development/SKILL.md`
- el template TailAdmin en `template/` y el frontend activo en `frontend/`.

## Seguridad de configuración

Todas las claves, usuarios, tokens, contraseñas, OAuth credentials, URLs de conexión y demás valores sensibles deben centralizarse en `.env`. `.env` está ignorado por Git; solo `.env.example` se versiona con placeholders. Nunca imprimir, hardcodear o comitear secretos.

Anti fuerza bruta (`backend/config/rate_limit.py`, cableado en `config/urls.py`): `login_view` limita 10 intentos fallidos por IP real (`X-Forwarded-For` siempre sobrescrito por Nginx, confiable en primer salto) en 15 min; `change_password_view` limita 5 verificaciones fallidas de la contraseña actual por usuario en 15 min; el contador se resetea al autenticar con éxito; excedido devuelve `429`. La `change_password_view` valida la contraseña nueva con `validate_password` (misma `AUTH_PASSWORD_VALIDATORS`: mínimo 12 + `CommonPasswordValidator`). El dev server Vite nunca debe servir "producción": la SPA se sirve del build estático (`location / → try_files`, assets con hash con caché immutable). Nginx agrega `X-Content-Type-Options`, `X-Frame-Options` y `Referrer-Policy`; además `SECURE_CONTENT_TYPE_NOSNIFF=True` y `X_FRAME_OPTIONS=DENY` a nivel Django.

RBAC (`backend/config/permissions.py`, roles en `apps/users/models.py`): todo viewset de negocio usa `RolePermission` — lectura para todo autenticado; `POST/PATCH/PUT` para `editor` y `admin`; `DELETE` solo `admin` (superusuario es siempre `admin` efectivo). Nuevos usuarios nacen `viewer` (mínimo privilegio, incluye OAuth); promoción vía `PATCH /api/auth/users/` (admin-only) o Django admin; un admin no puede degradarse a sí mismo. El frontend oculta los controles de escritura según `role` de `/api/auth/me/` con `frontend/src/hooks/usePermissions.ts` (cosmético; la autorización real es siempre backend-side y nace `viewer` como mínimo privilegio).

### Runbook: exponer en IP pública

1. En `.env`: `DEBUG=false`; agregar el host público a `ALLOWED_HOSTS` (coma-separado) — `CSRF_TRUSTED_ORIGINS` se deriva automáticamente de `ALLOWED_HOSTS` con `DEBUG=false`.
2. `docker compose up -d --force-recreate backend` (y `docker compose restart nginx` si Nginx cacheó la IP vieja del backend tras un recreate).
3. Con HTTPS (recomendado; p. ej. Caddy/Nginx-LetsEncrypt delante o `nginx` con certs): encender en `.env` `SECURE_SSL_REDIRECT=true`, `SESSION_COOKIE_SECURE=true`, `CSRF_COOKIE_SECURE=true`, `SECURE_HSTS_SECONDS=31536000`, `SECURE_HSTS_INCLUDE_SUBDOMAINS=true` (y `SECURE_HSTS_PRELOAD=true` si aplica) y recrear el backend.
4. Google OAuth: registrar en Google Cloud Console la URI de redirección `http(s)://<host>/auth/complete/google-oauth2/`.
5. Verificar que `DJANGO_SECRET_KEY` no sea un placeholder (rotarlo si lo es).
6. Pruebas destructivas: usar SIEMPRE usuarios humo con sufijo identificable, correr `python manage.py backup_data` (natural keys a `./backup`) **antes**, y borrar los objetos temporales al terminar (regla adoptada tras el incidente de la fila de humo eliminada por error).

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

Comandos de referencia operativa:

```bash
docker compose ps --format 'table {{.Service}}\t{{.Status}}'
docker compose up -d --build frontend
docker compose restart nginx
```

## Autenticación base

- Autenticación por **sesión** (cookies) con CSRF.
- **Google OAuth** bajo `/auth/` (social-django), con credenciales reales en `.env`.
  - `LOGIN_REDIRECT_URL = "/"` -> tras autenticar vuelve al dashboard SPA y el frontend recupera la sesión vía `me()`.
  - Callback: `http://localhost/auth/complete/google-oauth2/` (debe registrarse como Authorized redirect URI en Google Cloud Console).
- Backend: `login_view`, `me` y `logout_view` usan `@ensure_csrf_cookie` para emitir la cookie CSRF al navegador.
- `me` y `login_view` devuelven `is_local` y `auth_provider` (`"local"`/`"google"`) para que la UI muestre solo lo relevante a usuarios locales.
- Frontend: `AuthContext` carga la sesión vía `me()` y expone `user`, `login`, `loginWithGoogle`, `logout`; `ProtectedRoute` protege el layout autenticado y redirige a `/signin`.

## Patrones de UI/UX definidos

- **CRUD** sobre páginas por entidad, conectadas a la API bajo `/api/` con búsqueda y filtro por estado.
- **Modal de alta/edición** centrado (`centered`), con blur de fondo; **modal de eliminación** ocupa como máximo ~40% de la pantalla.
- Estado activo/inactivo se maneja con un componente `Switch` (toggle).
- **Selector con búsqueda** (input + lista desplegable filtrable): componente reutilizable `Combobox.tsx`.
- **Navegación jerárquica** en cascada dentro de un mismo modal (p. ej. universidad → unidad → carrera → plan): cada paso filtra el siguiente.
- **Menú lateral (sidebar)**: agrupa módulos en submenús; "Dashboard" es un enlace directo, no submenú.
- **Zoom persistido** por usuario en `localStorage` (clave `zoom`), inicializado de forma síncrona al montar.
- **Tema** dark/light persistido.

## Convenciones y pitfalls del frontend

- El `Button` de TailAdmin **no fija `type`**, por lo que dentro de un `<form>` actúa como `type="submit"`. Para botones que no deben hacer submit, usar `onSubmit={(e) => e.preventDefault()}` en el form o `type="button"` explícito.
- El servicio `frontend` monta `./frontend:/app` (bind-mount), por lo que los cambios se reflejan sin reconstruir la imagen; tras editar JS/TSX conviene validar con el build.
- El backend monta `./backend:/app`; **Gunicorn no hace hot-reload**, por lo que tras editar backend hay que reconstruir/reiniciar el servicio.
- Si la marca visual no parece actualizarse, forzar caché del navegador (`Ctrl + F5`).

## Problemas resueltos y decisiones de infraestructura

1. **PostgreSQL / volumen incompatibles**: el proyecto se inicializó con PostgreSQL 17, pero el volumen local estaba creado con una versión anterior. Se corrigió el compose para usar `postgres:16.10-alpine` y se evitó destruir datos previos de forma agresiva. La base arranca correctamente y los servicios siguen saludables.

2. **Nginx y headers del host**: el backend rechazaba solicitudes con `HTTP_HOST=academix_backend` o un host externo no consistente. Se ajustó la config del proxy inverso para conservar el host público y evitar errores de host/CSRF o errores de proxy.

3. **Estado de servicios y arranque**: hubo un problema inicial con 502 durante arranque porque Gunicorn no estaba listo aún. Se validó el estado real con `docker compose ps` y reinicios. El stack queda operativo.

4. **Frontend desactualizado / caché visual**: el contenedor entregaba una versión anterior del build. Se reconstruyó el frontend y se reinició Nginx. Si el navegador muestra contenido viejo, forzar recarga con `Ctrl + F5`.

5. **Branding visual**: el nombre visible del producto estaba incorrecto y se mostraba `LINEX` en lugar de `Academix`. Se actualizó el SVG del logo, el favicon y el título de la pestaña. El color principal es `#465FFF` (paleta TailAdmin). El texto visible del logo ahora es `Academix`.

6. **Volumen de desarrollo del frontend**: el servicio `frontend-dev` (perfil `dev`) monta `./frontend:/app` (+ ancla `/app/node_modules`) para que Vite refleje los cambios sin reconstruir la imagen; el servicio de producción `frontend` no monta nada (build horneado en la imagen).

7. **Cambio de contraseña en el perfil (usuarios locales) + arreglo de login**:
   - La sección "Cambiar contraseña" vive en el modal del perfil, visible solo si el usuario es local (`user.is_local`).
   - Bug clave: el `Button` de TailAdmin no fija `type`, así que dentro de un `<form>` actúa como `type="submit"`. Se añadió `onSubmit={(e) => e.preventDefault()}` al form del modal para evitar el submit nativo/recarga que rompía el flujo SPA (síntoma: "no me mostraba el menú" tras re-login).
   - Diagnóstico del reporte: el 400 en cambio de contraseña era "contraseña actual incorrecta"; el cambio no se aplicó por eso la clave anterior seguía funcionando. Verificado end-to-end (login 200 → change-password 200 → logout 200 → login con clave nueva 200).

## Archivos clave de infraestructura y UI

- `docker-compose.yml`: orquestación principal del entorno local.
- `backend/config/settings.py`: configuración global de Django, seguridad y entorno.
- `frontend/src/api/client.ts`: cliente fetch con cookies, CSRF y manejo de errores.
- `frontend/src/context/AuthContext.tsx`: estado de sesión, login, logout y Google.
- `frontend/src/context/ThemeContext.tsx`: tema dark/light y zoom persistido.
- `frontend/src/components/common/ProtectedRoute.tsx`: protección de rutas autenticadas.
- `frontend/src/components/ui/modal/index.tsx`: Modal con props `centered`/`isFullscreen`.
- `frontend/src/components/form/Combobox.tsx`: selector reutilizable con búsqueda.
- `frontend/src/layout/AppSidebar.tsx`: navegación principal por módulos.
- `frontend/index.html`: favicon y título de la pestaña.
- `frontend/public/images/logo/*.svg`: assets del logo.
- `.env` y `.env.example`: secretos y configuración centralizada.

## Reglas de desarrollo

- No hardcodear secretos ni valores sensibles en código.
- Mantener `.env` fuera del control de versiones; solo `.env.example` debe versionarse.
- Insumos de carga manual (planillas, JSON de origen) van en `auto/`, también ignorada por Git, igual que `autoskills/`, `./backup/*.json` y `backend/media/`.
- Antes de editar, formular una hipótesis simple y ejecutar una validación breve.
- Tras cambios, ejecutar al menos: validación del backend (`manage.py check` o tests) o build del frontend si se modifica UI.
- Si se trabaja con Docker, validar el estado real con `docker compose ps` y reintentar con `docker compose up -d --build <servicio>` cuando sea requerido.

## Validaciones de la base confirmadas

- `python3 backend/manage.py check` -> OK.
- `python3 backend/manage.py test` -> tests pasando.
- `cd frontend && npm run build` -> build correcto con warnings existentes no bloqueantes (chunk > 500 kB y un warning CSS de SimpleBar).
- `docker compose ps --format 'table {{.Service}}\t{{.Status}}'` -> servicios activos.
- `curl -fsS http://localhost/images/logo/academix-logo.svg | grep -E '465FFF|Academix'` -> asset público con texto y color correctos.
