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

## Backup y restauración de datos

Los datos de negocio (universidades, unidades, sedes, carreras, planes, áreas, materias y nomencladores) se respaldan como JSON en `./backup` con *natural keys*: cada registro se identifica por sus códigos/combinaciones únicas, no por su `id`, de modo que la restauración funciona aunque la estructura de la base haya cambiado (campos agregados/quitados, IDs nuevos).

```bash
# Backups
./scripts/backup.sh                                    # respalda en ./backup/academix_backup_<fecha>.json
./scripts/backup.sh --output=./backup/mi-backup.json   # nombre/ruta personalizado

# Restauración (fusiona por natural key: actualiza lo existente, crea lo nuevo)
./scripts/restore.sh                                   # usa el backup más reciente de ./backup
./scripts/restore.sh --input=./backup/mi-backup.json   # un archivo específico
./scripts/restore.sh --yes                             # sin confirmación (útil en scripts)
```

Los dos scripts envuelven comandos de Django, equivalentes a:

```bash
docker compose exec backend python manage.py backup_data
docker compose exec backend python manage.py restore_data --yes
```

La restauración tolera cambios de esquema: solo aplica los campos presentes tanto en el JSON como en el modelo actual; los campos nuevos quedan con su valor por defecto y los modelos eliminados se ignoran. Los backups (`.json`) no se versionan en Git; la carpeta `./backup` está montada en el contenedor `backend`.

## Desarrollo asistido por IA

Las reglas globales están en [.github/AGENTS.md](.github/AGENTS.md). Los subagentes especializados están en [.github/agents/academix-backend.agent.md](.github/agents/academix-backend.agent.md) y [.github/agents/academix-frontend.agent.md](.github/agents/academix-frontend.agent.md). Ambos deben cargar los skills locales indicados antes de trabajar.

## Validación

```bash
python3 -m compileall -q backend
docker compose config --quiet
docker compose exec backend python manage.py check
docker compose exec backend python manage.py test
```
