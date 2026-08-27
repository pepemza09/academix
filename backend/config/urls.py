from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.routers import DefaultRouter

from apps.academics.models import AcademicUnit, University


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ["id", "name", "short_name", "is_active"]


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [IsAuthenticated]


class AcademicUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicUnit
        fields = ["id", "code", "short_name", "name", "university", "is_active"]
        read_only_fields = ["university"]


class AcademicUnitViewSet(viewsets.ModelViewSet):
    queryset = AcademicUnit.objects.select_related("university").all()
    serializer_class = AcademicUnitSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        university, _ = University.objects.get_or_create(name="Universidad")
        serializer.save(university=university)


router = DefaultRouter()
router.register("universities", UniversityViewSet, basename="university")
router.register("academic-units", AcademicUnitViewSet, basename="academic-unit")


@require_http_methods(["GET"])
def health(request):
    return JsonResponse({"status": "ok", "service": "academix-api"})


@require_http_methods(["POST"])
@ensure_csrf_cookie
def login_view(request):
    import json
    payload = json.loads(request.body or "{}")
    user = authenticate(request, username=payload.get("username"), password=payload.get("password"))
    if user is None:
        return JsonResponse({"detail": "Credenciales inválidas."}, status=401)
    login(request, user)
    return JsonResponse({"id": user.id, "username": user.username, "email": user.email})


@ensure_csrf_cookie
def me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Autenticación requerida."}, status=401)
    return JsonResponse({"id": request.user.id, "username": request.user.username, "email": request.user.email})


@require_http_methods(["POST"])
@ensure_csrf_cookie
def logout_view(request):
    logout(request)
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("api/", include(router.urls)),
    path("api/auth/login/", login_view),
    path("api/auth/me/", me),
    path("api/auth/logout/", logout_view),
    path("auth/", include("social_django.urls", namespace="social")),
]
