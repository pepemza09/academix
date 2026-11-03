from django.conf import settings
from django.db import migrations, models


def bootstrap_roles(apps, schema_editor):
    """Promueve a ADMIN a superusuarios y staff existentes y garantiza
    un perfil para cada usuario (los nuevos usuarios nacen VIEWER vía señal)."""
    Profile = apps.get_model("users", "Profile")
    User = apps.get_model(settings.AUTH_USER_MODEL)
    for user in User.objects.all():
        role = "admin" if user.is_superuser or user.is_staff else "viewer"
        profile, _ = Profile.objects.get_or_create(user=user, defaults={"role": role})
        if profile.role != role and (user.is_superuser or user.is_staff):
            profile.role = role
            profile.save(update_fields=["role"])


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="profile",
            options={"verbose_name": "perfil"},
        ),
        migrations.AddField(
            model_name="profile",
            name="role",
            field=models.CharField(
                choices=[
                    ("admin", "Administrador (crea, edita y elimina)"),
                    ("editor", "Editor (crea y edita, no elimina)"),
                    ("viewer", "Consulta (solo lectura)"),
                ],
                default="viewer",
                max_length=16,
                verbose_name="rol",
            ),
        ),
        migrations.RunPython(bootstrap_roles, migrations.RunPython.noop),
    ]
