#!/usr/bin/env bash
# Crea un backup JSON de los datos de negocio en ./backup.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose exec -T backend python manage.py backup_data "$@"