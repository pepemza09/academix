"""Backup de los datos de negocio (dominio académico) a JSON.

Uso:
    python manage.py backup_data
    python manage.py backup_data --output=../backup
"""

import json
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from ..backup_utils import export_data


class Command(BaseCommand):
    help = (
        "Exporta los datos de negocio (dominio academics) a un archivo JSON "
        "con natural keys, listo para reimportar con restore_data."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            help=(
                "Directorio o archivo de salida. Por defecto es "
                "./backup/academix_backup_<fecha>.json"
            ),
        )

    def get_default_output(self):
        base = Path(settings.BASE_DIR).parent / "backup"
        base.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return base / f"academix_backup_{stamp}.json"

    def handle(self, *args, **options):
        output = options.get("output")
        if output:
            out_path = Path(output)
            if out_path.is_dir() or str(out_path).endswith(("/", "\\")) or not out_path.suffix:
                out_path.mkdir(parents=True, exist_ok=True)
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_path = out_path / f"academix_backup_{stamp}.json"
        else:
            out_path = self.get_default_output()

        out_path.parent.mkdir(parents=True, exist_ok=True)

        payload = export_data()

        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

        model_counts = {
            name: len(records) for name, records in payload["models"].items()
        }
        total = sum(model_counts.values())
        self.stdout.write(self.style.SUCCESS(f"Backup creado: {out_path}"))
        self.stdout.write(
            f"Registros por modelo: "
            + ", ".join(f"{name}={n}" for name, n in model_counts.items())
        )
        self.stdout.write(self.style.SUCCESS(f"Total: {total} registros."))