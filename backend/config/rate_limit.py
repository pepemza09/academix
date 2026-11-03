"""Protección anti fuerza bruta para las vistas de autenticación.

`login_view` y `change_password_view` son vistas Django planas, así que no
atraviesan el throttling de DRF. Este módulo implementa límites de intentos
fallidos usando el caché (Redis en producción, LocMem en tests):

- login: por IP real del cliente (Nginx sobrescribe X-Forwarded-For, por lo
  que su primer valor es confiable).
- cambio de contraseña: por usuario, sobre la verificación de la contraseña
  actual (la única operación secreta del endpoint).

El contador se resetea al autenticar con éxito.
"""

from django.core.cache import cache

LOGIN_FAIL_WINDOW_SECONDS = 15 * 60
LOGIN_FAIL_MAX_ATTEMPTS = 10
PASSWORD_FAIL_WINDOW_SECONDS = 15 * 60
PASSWORD_FAIL_MAX_ATTEMPTS = 5


def client_ip(request):
    """IP del cliente: primer salto de X-Forwarded-For o REMOTE_ADDR."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        first = forwarded.split(",")[0].strip()
        if first:
            return first
    return request.META.get("REMOTE_ADDR", "")


def login_fail_key(request):
    return f"rl:login:ip:{client_ip(request)}"


def password_fail_key(user):
    return f"rl:pwfail:user:{user.pk}"


def attempts_exceeded(bucket_key, max_attempts):
    """True si el contador del bucket alcanzó el límite."""
    return (cache.get(bucket_key) or 0) >= max_attempts


def register_attempt(bucket_key, window_seconds):
    """Incrementa el contador del bucket y devuelve el total actual."""
    if not cache.add(bucket_key, 1, window_seconds):
        try:
            return cache.incr(bucket_key)
        except ValueError:
            cache.set(bucket_key, 1, window_seconds)
            return 1
    return 1


def reset_attempts(bucket_key):
    cache.delete(bucket_key)
