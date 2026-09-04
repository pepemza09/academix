"""Restaura los datos de negocio (dominio académico) desde un JSON.

Uso:
    python manage.py restore_data
    python manage.py restore_data --input=../backup/academix_backup_20260904_120000.json
    python manage.py restore_data --yes   (sin confirmación)

Fusiona por natural key: los registros existentes se actualizan y los
nuevos se crean. Solo se aplican los campos presentes tanto en el backup
como en el modelo actual, por lo que tolera cambios de esquema.
"""

import json
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ..backup_utils import import_data


class Command(BaseCommand):
    help = (
        "Carga/fusiona un backup JSON del dominio academics. Por defecto "
        "usa el backup más reciente de ./backup."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            help="Archivo JSON a cargar (por defecto el más reciente de ./backup).",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="No preguntar confirmación antes de cargar.",
        )

    def get_default_input(self):
        backup_dir = Path(settings.BASE_DIR).parent / "backup"
        if not backup_dir.is_dir():
            raise CommandError(
                f"No existe el directorio de backups: {backup_dir}"
            )
        candidates = sorted(backup_dir.glob("academix_backup_*.json"))
        if not candidates:
            raise CommandError(
                f"No hay archivos academix_backup_*.json en {backup_dir}"
            )
        return candidates[-1]

    def handle(self, *args, **options):
        input_arg = options.get("input")
        in_path = Path(input_arg) if input_arg else self.get_default_input()

        if not in_path.is_file():
            raise CommandError(f"No existe el archivo: {in_path}")

        with open(in_path, encoding="utf-8") as fh:
            try:
                payload = json.load(fh)
            except json.JSONDecodeError as exc:
                raise CommandError(
                    f"El archivo {in_path} no es JSON válido: {exc}"
                ) from exc

        if not options["yes"]:
            if sys.stdin.isatty():
                confirm = input(
                    f"¿Cargar el backup {in_path}? Los registros se "
                    "fusionarán por natural key [y/N]: "
                ).strip().lower()
                if confirm not in ("y", "yes"):
                    self.stdout.write("Carga cancelada.")
                    return
            else:
                raise CommandError(
                    "Confirmación requerida. Usa --yes para restaurar "
                    "sin preguntar."
                )

        summary = import_data(payload)

        total_created = sum(c for c, _ in summary.values())
        total_updated = sum(u for _, u in summary.values())
        self.stdout.write(self.style.SUCCESS(f"Backup cargado: {in_path}"))
        for model_name, (created, updated) in summary.items():
            self.stdout.write(
                f"  {model_name}: {created} creados, {updated} actualizados"
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Total: {total_created} creados, {total_updated} actualizados."
            )
        )