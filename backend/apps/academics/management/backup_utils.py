"""Serialización de negocio (dominio ``academics``) con natural keys.

El backup guarda cada objeto por su *natural key* (combo de campos únicos
dentro de su padre) en lugar del ``id``, de modo que la restauración
funciona aunque los IDs cambien o la estructura de la base evolucione.

La restauración solo aplica los campos que existan tanto en el JSON como en
el modelo actual; los campos nuevos quedan con su valor por defecto y los
campos eliminados se ignoran.
"""

import json

from django.apps import apps
from django.db import models

APP_LABEL = "academics"

# Orden de dependencia: los hijos se cargan después que sus padres.
MODEL_ORDER = [
    "Nomenclador",
    "University",
    "AcademicUnit",
    "Campus",
    "Career",
    "StudyPlan",
    "StudyArea",
    "Subject",
]

# Natural key por modelo: campos (incluidos FK) que identifican al objeto.
NATURAL_KEYS = {
    "Nomenclador": ["discipline", "subdiscipline", "specialty"],
    "University": ["name"],
    "AcademicUnit": ["university", "code"],
    "Campus": ["academic_unit", "code"],
    "Career": ["academic_unit", "code"],
    "StudyPlan": ["career", "code"],
    "StudyArea": ["study_plan", "name"],
    "Subject": ["study_area", "code"],
}

BACKUP_VERSION = 1


def get_model(name):
    return apps.get_model(APP_LABEL, name)


def available_models():
    """Modelos de la orden actual que siguen existiendo en el proyecto."""
    return [name for name in MODEL_ORDER if get_model(name) is not None]


def _natural_key_dict(instance, seen=None):
    """Natural key de una instancia como dict anidable (FK se anidan)."""
    model_name = instance.__class__.__name__
    seen = seen or set()
    if instance.pk is None:
        return None
    marker = (model_name, instance.pk)
    if marker in seen:
        raise ValueError(
            f"Natural key cíclica detectada en {model_name}#{instance.pk}"
        )
    seen = seen | {marker}

    record = {}
    for field_name in NATURAL_KEYS[model_name]:
        field = instance._meta.get_field(field_name)
        if isinstance(field, models.ForeignKey):
            related = getattr(instance, field_name)
            record[field_name] = (
                _natural_key_dict(related, seen) if related else None
            )
        else:
            record[field_name] = getattr(instance, field_name)
    return record


def _serialize_instance(instance):
    """Todos los campos editables del objeto; FK/M2M como natural keys."""
    data = {}
    for field in instance._meta.get_fields():
        if isinstance(field, models.ManyToManyField):
            related = getattr(instance, field.name)
            data[field.name] = [
                ref
                for ref in (_natural_key_dict(obj) for obj in related.all())
                if ref is not None
            ]
        elif isinstance(field, models.ForeignKey):
            related = getattr(instance, field.name, None)
            data[field.name] = (
                _natural_key_dict(related) if related else None
            )
        elif (
            field.concrete
            and field.editable
            and not field.primary_key
            and not isinstance(field, (models.AutoField,))
        ):
            data[field.name] = getattr(instance, field.name)
    return data


def export_data():
    """Devuelve el dict que se escribe como JSON de backup."""
    payload = {
        "version": BACKUP_VERSION,
        "models": {},
    }
    for model_name in available_models():
        model = get_model(model_name)
        payload["models"][model_name] = [
            _serialize_instance(obj) for obj in model.objects.all()
        ]
    return payload


def _resolve(model_name, nk, registry):
    """Resuelve una natural key dict a la instancia real (con caché)."""
    key = (model_name, json.dumps(nk, sort_keys=True, ensure_ascii=False))
    cached = registry.get(key)
    if cached is not None:
        return cached
    model = get_model(model_name)
    if model is None:
        raise ValueError(f"Modelo desconocido en backup: {model_name}")
    kwargs = {}
    for field_name in NATURAL_KEYS[model_name]:
        field = model._meta.get_field(field_name)
        if isinstance(field, models.ForeignKey):
            kwargs[field_name] = _resolve(
                field.related_model.__name__, nk[field_name], registry
            )
        else:
            kwargs[field_name] = nk[field_name]
    obj = model.objects.get(**kwargs)
    registry[key] = obj
    return obj


def import_data(payload):
    """Carga/fusiona los registros del JSON en la base actual.

    Devuelve un resumen {modelo: (creados, actualizados)}.
    """
    if payload.get("version") != BACKUP_VERSION:
        raise ValueError(
            f"Versión de backup no soportada: {payload.get('version')}"
        )

    registry: dict = {}
    summary: dict[str, tuple[int, int]] = {}

    for model_name, records in payload["models"].items():
        model = get_model(model_name)
        if model is None:
            # El modelo fue eliminado del proyecto: se ignora sin romper.
            continue

        created_count = 0
        updated_count = 0
        for record in records:
            lookup = {}
            for field_name in NATURAL_KEYS[model_name]:
                field = model._meta.get_field(field_name)
                if isinstance(field, models.ForeignKey):
                    lookup[field_name] = _resolve(
                        field.related_model.__name__,
                        record[field_name],
                        registry,
                    )
                else:
                    lookup[field_name] = record[field_name]

            values = {}
            for field in model._meta.get_fields():
                if (
                    field.name in record
                    and field.concrete
                    and field.editable
                    and not field.primary_key
                    and field.name not in NATURAL_KEYS[model_name]
                    and not isinstance(field, models.ManyToManyField)
                ):
                    value = record[field.name]
                    if isinstance(field, models.ForeignKey):
                        values[field.name] = (
                            None
                            if value is None
                            else _resolve(
                                field.related_model.__name__,
                                value,
                                registry,
                            )
                        )
                    else:
                        values[field.name] = value

            try:
                obj = model.objects.get(**lookup)
                created = False
            except model.DoesNotExist:
                obj = model(**lookup, **values)
                created = True

            if created:
                obj.save()
            else:
                update_fields = [
                    field_name
                    for field_name, value in values.items()
                    if getattr(obj, field_name) != value
                ]
                for field_name in update_fields:
                    setattr(obj, field_name, values[field_name])
                if update_fields:
                    obj.save(update_fields=update_fields)

            for field in model._meta.get_fields():
                if isinstance(field, models.ManyToManyField) and field.name in record:
                    related_model = field.related_model
                    manager = getattr(obj, field.name)
                    new_ids = [
                        _resolve(
                            related_model.__name__, nk, registry
                        ).pk
                        for nk in record[field.name]
                    ]
                    if set(manager.values_list("pk", flat=True)) != set(new_ids):
                        manager.set(new_ids)

            plain_nk = {k: record[k] for k in NATURAL_KEYS[model_name]}
            registry[
                (
                    model_name,
                    json.dumps(plain_nk, sort_keys=True, ensure_ascii=False),
                )
            ] = obj
            if created:
                created_count += 1
            else:
                updated_count += 1

        summary[model_name] = (created_count, updated_count)

    return summary