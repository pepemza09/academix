#!/usr/bin/env bash
# Restaura (fusiona por natural key) un backup JSON en la base de datos.
# Por defecto usa el backup más reciente de ./backup.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose exec -T backend python manage.py restore_data "$@"