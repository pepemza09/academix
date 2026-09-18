"""Importa el nomenclador de disciplinas (UNESCO) desde archivos JSON.

El formato esperado es una lista de objetos por archivo:

    [
        {"disciplina": "1 - CIENCIAS NATURALES Y EXACTAS",
         "subdisciplina": "01 - ASTRONOMIA",
         "especialidad": "01 - ASTROFISICA",
         "activo": true},
        ...
    ]

Uso:
    python manage.py import_nomenclador
    python manage.py import_nomenclador --directory=../backup
    python manage.py import_nomenclador --pattern=ciencias

Los nombres de archivo se usan solo como etiqueta de informe. La operación
es idempotente: fusiona por natural key (disciplina, subdisciplina,
especialidad); los registros existentes se actualizan y los nuevos se crean.
"""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.academics.models import Nomenclador

# Claves esperadas en cada registro y a qué campo del modelo corresponden.
FIELD_MAP = {
    "disciplina": "discipline",
    "subdisciplina": "subdiscipline",
    "especialidad": "specialty",
    "activo": "is_active",
}
REQUIRED_KEYS = ("disciplina", "subdisciplina", "especialidad")


class Command(BaseCommand):
    help = (
        "Carga/fusiona el nomenclador de disciplinas desde archivos JSON "
        "(formato disciplina/subdisciplina/especialidad)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--directory",
            help="Carpeta con los archivos JSON (por defecto ../backup).",
        )
        parser.add_argument(
            "--pattern",
            help="Subcadena para filtrar archivos JSON por nombre.",
        )

    def get_directory(self, option):
        if option:
            path = Path(option)
        else:
            path = Path(settings.BASE_DIR).parent / "backup"
        if not path.is_dir():
            raise CommandError(f"No existe el directorio: {path}")
        return path

    def iter_files(self, directory, pattern):
        for path in sorted(directory.glob("*.json")):
            if pattern and pattern.lower() not in path.name.lower():
                continue
            yield path

    def ingest_file(self, path):
        raw = path.read_bytes()
        try:
            payload = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, 0, 0, f"JSON inválido: {exc}"

        if not isinstance(payload, list):
            return None, 0, 0, "El archivo no contiene una lista de registros."

        created_count = 0
        updated_count = 0
        for index, record in enumerate(payload, start=1):
            if not isinstance(record, dict):
                return None, created_count, updated_count, (
                    f"Registro {index} no es un objeto."
                )
            missing = [k for k in REQUIRED_KEYS if k not in record]
            if missing:
                return None, created_count, updated_count, (
                    f"Registro {index} sin claves requeridas: {missing}."
                )

            values = {
                model_field: record[json_key]
                for json_key, model_field in FIELD_MAP.items()
            }
            is_active = values.pop("is_active")
            if not isinstance(is_active, bool):
                is_active = True

            obj, created = Nomenclador.objects.get_or_create(
                discipline=values["discipline"],
                subdiscipline=values["subdiscipline"],
                specialty=values["specialty"],
                defaults={"is_active": is_active},
            )
            if created:
                created_count += 1
            else:
                if obj.is_active != is_active:
                    obj.is_active = is_active
                    obj.save(update_fields=["is_active", "updated_at"])
                updated_count += 1

        return path, created_count, updated_count, None

    def handle(self, *args, **options):
        directory = self.get_directory(options.get("directory"))
        pattern = options.get("pattern")

        files = list(self.iter_files(directory, pattern))
        if not files:
            raise CommandError(f"No hay archivos JSON en: {directory}")

        total_created = 0
        total_updated = 0
        ignored = []

        for path in files:
            result = self.ingest_file(path)
            file_path, created_count, updated_count, error = result
            if error:
                ignored.append(f"{path.name}: {error}")
                continue
            total_created += created_count
            total_updated += updated_count
            self.stdout.write(
                f"  {path.name}: {created_count} creados, "
                f"{updated_count} actualizados"
            )

        if ignored:
            for line in ignored:
                self.stdout.write(self.style.WARNING(f"  Omitido: {line}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Nomenclador: {total_created} creados, "
                f"{total_updated} actualizados."
            )
        )