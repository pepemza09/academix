"""Permisos RBAC para la API de negocio.

Roles sobre `Profile.role`:

- admin:  lectura + creación + edición + eliminación.
- editor: lectura + creación + edición (no eliminación).
- viewer: solo lectura.

Los superusuarios siempre tienen rol efectivo admin. Toda la capa
autoritativa vive aquí; los viewsets solo declaran esta clase.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.models import Profile, user_role


class RolePermission(BasePermission):
    """Autenticado con SAFE_METHODS; escritura según rol; DELETE solo admin."""

    message = "No tenés permisos para esta operación."

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        role = user_role(user)
        if role == Profile.Role.ADMIN:
            return True
        if request.method == "DELETE":
            return False
        return role == Profile.Role.EDITOR
