# Academix

Academix es la base de una plataforma para la gestión académica de una universidad. La primera vertical modela una universidad con N unidades académicas, cada una con código, nombre corto, nombre completo y estado.

## Arquitectura

- `backend/`: Django 5 + Django REST Framework, PostgreSQL, Redis y Gunicorn.
- `frontend/`: React 19 + Vite + Tailwind 4, basado en el template TailAdmin incluido en `template/`.
- `nginx/`: proxy inverso para frontend, API y OAuth.
- `docker-compose.yml`: servicios `nginx`, `frontend`, `backend`, `db` y `redis`.

## Arranque local

Requisitos: Docker Engine y Docker Compose.

```bash
cp .env.example .env
# Edita .env y establece un DJANGO_SECRET_KEY propio.
docker compose up --build
```

La aplicación queda disponible en `http://localhost`. La API responde en `/api/` y el healthcheck en `/health/`.

Para crear un administrador:

```bash
docker compose exec backend python manage.py createsuperuser
```

## Autenticación

- Usuario local: `POST /api/auth/login/` con `username` y `password`.
- Sesión actual: `GET /api/auth/me/`.
- Cierre de sesión: `GET /api/auth/logout/`.
- Google OAuth: `/auth/login/google-oauth2/`, configurado con `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` en `.env`.

En producción hay que configurar HTTPS, dominios permitidos, credenciales OAuth y cookies seguras antes de desplegar.

## Seguridad de secretos

Todos los secretos, usuarios, contraseñas, tokens y URLs de conexión se leen desde `.env`. El archivo `.env` está excluido por Git; solo `.env.example` se versiona con placeholders. Nunca introduzcas credenciales en código, logs, commits o imágenes Docker.

## Desarrollo asistido por IA

Las reglas globales están en [.github/AGENTS.md](.github/AGENTS.md). Los subagentes especializados están en [.github/agents/academix-backend.agent.md](.github/agents/academix-backend.agent.md) y [.github/agents/academix-frontend.agent.md](.github/agents/academix-frontend.agent.md). Ambos deben cargar los skills locales indicados antes de trabajar.

## Validación

```bash
python3 -m compileall -q backend
docker compose config --quiet
docker compose exec backend python manage.py check
docker compose exec backend python manage.py test
```
