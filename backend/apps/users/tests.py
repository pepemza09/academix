import json

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from apps.users.models import Profile, user_role

User = get_user_model()


class AuthThrottleTests(TestCase):
    """Fuerza bruta: límites de intentos fallidos y reseteo al acertar."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="tester",
            password="testpass123456",
            email="tester@example.com",
        )

    def _login(self, password="wrongpass"):
        return self.client.post(
            reverse("login"),
            data=json.dumps({"username": "tester", "password": password}),
            content_type="application/json",
        )

    def test_login_success_returns_payload(self):
        resp = self._login("testpass123456")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["username"], "tester")

    def test_bad_credentials_return_401(self):
        resp = self._login()
        self.assertEqual(resp.status_code, 401)

    def test_login_throttles_after_max_attempts(self):
        from config.rate_limit import LOGIN_FAIL_MAX_ATTEMPTS

        for _ in range(LOGIN_FAIL_MAX_ATTEMPTS - 1):
            resp = self._login()
            self.assertEqual(resp.status_code, 401)
        resp = self._login()
        self.assertEqual(resp.status_code, 401)

        # Agotado el límite, incluso con credenciales correctas se bloquea.
        resp = self._login()
        self.assertEqual(resp.status_code, 429)

    def test_successful_login_resets_failed_attempts(self):
        self._login()
        self._login()
        resp = self._login("testpass123456")
        self.assertEqual(resp.status_code, 200)

        # Tras el reseteo, vuelven a aceptarse intentos fallidos sin 429.
        resp = self._login()
        self.assertEqual(resp.status_code, 401)

    def _change_password(self, current_password="wrongpass", new_password=None):
        return self.client.post(
            reverse("change-password"),
            data=json.dumps(
                {
                    "current_password": current_password,
                    "new_password": new_password or "newpass987654",
                }
            ),
            content_type="application/json",
        )

    def test_change_password_wrong_current_returns_400(self):
        self.client.force_login(self.user)
        resp = self._change_password()
        self.assertEqual(resp.status_code, 400)

    def test_change_password_throttles_after_max_attempts(self):
        from config.rate_limit import PASSWORD_FAIL_MAX_ATTEMPTS

        self.client.force_login(self.user)
        for _ in range(PASSWORD_FAIL_MAX_ATTEMPTS):
            resp = self._change_password()
            self.assertEqual(resp.status_code, 400)

        # Agotado el límite, la verificación se bloquea por usuario
        # aunque la contraseña actual sea correcta.
        resp = self._change_password("testpass123456")
        self.assertEqual(resp.status_code, 429)

    def test_login_payload_includes_role(self):
        resp = self._login("testpass123456")
        self.assertEqual(resp.json()["role"], Profile.Role.VIEWER)


class RolePermissionTests(TestCase):
    """Autorización RBAC: viewer solo lee, editor crea/edita, admin todo."""

    def setUp(self):
        cache.clear()
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="superadmin123",
        )
        self.viewer = User.objects.create_user(
            username="viewer",
            password="viewpass1234",
        )
        self.editor = User.objects.create_user(
            username="editor",
            password="editpass1234",
        )
        Profile.objects.filter(user=self.editor).update(role=Profile.Role.EDITOR)

    def _auth_as(self, user):
        self.client.force_login(user)

    def _university(self, name="Universidad RBAC"):
        return {
            "name": name,
            "short_name": "URBAC",
            "is_active": True,
        }

    def _post_university(self):
        return self.client.post(
            reverse("university-list"),
            data=json.dumps(self._university()),
            content_type="application/json",
        )

    def _delete_university(self, obj_id=None):
        if obj_id is None:
            created = self._post_university()
            obj_id = created.json()["id"]
        return self.client.delete(reverse("university-detail", args=[obj_id]))

    def test_anonymous_gets_401_or_403(self):
        resp = self.client.get(reverse("university-list"))
        self.assertIn(resp.status_code, (401, 403))

    def test_anonymous_post_gets_401_or_403(self):
        resp = self.client.post(
            reverse("university-list"),
            data=json.dumps(self._university()),
            content_type="application/json",
        )
        self.assertIn(resp.status_code, (401, 403))

    def test_viewer_can_read_but_not_write(self):
        self._auth_as(self.viewer)
        resp = self.client.get(reverse("university-list"))
        self.assertEqual(resp.status_code, 200)
        resp = self._post_university()
        self.assertEqual(resp.status_code, 403)

    def test_viewer_cannot_delete(self):
        self._auth_as(self.admin)
        created = self._post_university()
        obj_id = created.json()["id"]
        self._auth_as(self.viewer)
        resp = self.client.delete(reverse("university-detail", args=[obj_id]))
        self.assertEqual(resp.status_code, 403)

    def test_editor_can_write_but_not_delete(self):
        self._auth_as(self.editor)
        resp = self._post_university()
        self.assertEqual(resp.status_code, 201)
        resp = self._delete_university(resp.json()["id"])
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_add_and_rem(self):
        self._auth_as(self.admin)
        resp = self._post_university()
        self.assertEqual(resp.status_code, 201)
        resp = self._delete_university(resp.json()["id"])
        self.assertEqual(resp.status_code, 204)

    def test_superuser_role_is_admin(self):
        self.assertEqual(user_role(self.admin), Profile.Role.ADMIN)


class RoleApiTests(TestCase):
    """Endpoint admin-only de gestión de roles (/api/auth/users/)."""

    def setUp(self):
        cache.clear()
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="superadmin123",
        )
        self.viewer = User.objects.create_user(
            username="viewer",
            password="viewpass1234",
        )
        self.other = User.objects.create_user(
            username="other",
            password="otherpass1234",
        )

    def _patch(self, user_id, role):
        return self.client.patch(
            reverse("users"),
            data=json.dumps({"user_id": user_id, "role": role}),
            content_type="application/json",
        )

    def test_requires_authentication(self):
        resp = self.client.get(reverse("users"))
        self.assertEqual(resp.status_code, 401)

    def test_requires_admin(self):
        self.client.force_login(self.viewer)
        resp = self.client.get(reverse("users"))
        self.assertEqual(resp.status_code, 403)
        resp = self._patch(self.viewer.id, Profile.Role.EDITOR)
        self.assertEqual(resp.status_code, 403)

    def test_admin_lists_users_with_roles(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("users"))
        self.assertEqual(resp.status_code, 200)
        roles = {u["username"]: u["role"] for u in resp.json()["users"]}
        self.assertEqual(roles["viewer"], Profile.Role.VIEWER)
        self.assertEqual(roles["admin"], Profile.Role.ADMIN)

    def test_admin_assigns_role(self):
        self.client.force_login(self.admin)
        resp = self._patch(self.viewer.id, Profile.Role.EDITOR)
        self.assertEqual(resp.status_code, 200)
        profile = Profile.objects.get(user_id=self.viewer.id)
        self.assertEqual(profile.role, Profile.Role.EDITOR)

    def test_rejects_unknown_role(self):
        self.client.force_login(self.admin)
        resp = self._patch(self.viewer.id, "sithlord")
        self.assertEqual(resp.status_code, 400)

    def test_admin_cannot_demote_self(self):
        self.client.force_login(self.admin)
        resp = self._patch(self.admin.id, Profile.Role.VIEWER)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(user_role(self.admin), Profile.Role.ADMIN)


class ChangePasswordPolicyTests(TestCase):
    """La política de /api/auth/change-password/ usa AUTH_PASSWORD_VALIDATORS."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="tester",
            password="testpass123456",
        )

    def _change(self, new_password):
        self.client.force_login(self.user)
        return self.client.post(
            reverse("change-password"),
            data=json.dumps(
                {
                    "current_password": "testpass123456",
                    "new_password": new_password,
                }
            ),
            content_type="application/json",
        )

    def test_rejects_short_password(self):
        resp = self._change("abc123")
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(User.objects.get(username="tester").check_password("abc123"))

    def test_rejects_common_password(self):
        resp = self._change("password123456")
        self.assertEqual(resp.status_code, 400)

    def test_accepts_strong_password(self):
        resp = self._change("Nueva-Clave-Fuerte-9x")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            User.objects.get(username="tester").check_password("Nueva-Clave-Fuerte-9x")
        )
