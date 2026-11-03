from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Perfil por usuario: avatar y rol para el control RBAC de la API."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador (crea, edita y elimina)"
        EDITOR = "editor", "Editor (crea y edita, no elimina)"
        VIEWER = "viewer", "Consulta (solo lectura)"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
    )
    role = models.CharField(
        "rol",
        max_length=16,
        choices=Role.choices,
        default=Role.VIEWER,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "perfil"

    def __str__(self) -> str:
        return f"Perfil de {self.user.username}"


def user_role(user) -> str:
    """Rol efectivo del usuario para la capa de permisos.

    Los superusuarios siempre son ADMIN. Sin perfil (creación directa de
    usuario sin señal o fixtures) se aplica el mínimo privilegio: VIEWER.
    """
    if user.is_superuser:
        return Profile.Role.ADMIN
    profile = Profile.objects.filter(user=user).only("role").first()
    return profile.role if profile else Profile.Role.VIEWER


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile_for_user(sender, instance, created, **kwargs) -> None:
    """Todo usuario nuevo tiene un perfil con el rol mínimo VIEWER."""
    if created:
        Profile.objects.get_or_create(user=instance, defaults={"role": Profile.Role.VIEWER})
