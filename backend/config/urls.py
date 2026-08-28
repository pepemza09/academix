from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from apps.academics.models import AcademicUnit, Campus, Career, University


class UniversitySerializer(serializers.ModelSerializer):
    academic_unit_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = University
        fields = ["id", "name", "short_name", "is_active", "academic_unit_count"]


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.annotate(
        academic_unit_count=Count("academic_units")
    )
    serializer_class = UniversitySerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        university = self.get_object()
        if university.academic_units.exists():
            return Response(
                {
                    "detail": "No se puede eliminar una universidad que tiene unidades académicas asociadas."
                },
                status=400,
            )
        return super().destroy(request, *args, **kwargs)


class AcademicUnitSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(
        source="university.name", read_only=True
    )
    campus_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AcademicUnit
        fields = [
            "id",
            "code",
            "short_name",
            "name",
            "university",
            "university_name",
            "campus_count",
            "is_active",
        ]


class AcademicUnitViewSet(viewsets.ModelViewSet):
    queryset = AcademicUnit.objects.select_related("university").annotate(
        campus_count=Count("campuses")
    )
    serializer_class = AcademicUnitSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        academic_unit = self.get_object()
        if academic_unit.campuses.exists():
            return Response(
                {
                    "detail": "No se puede eliminar una unidad académica que tiene sedes asociadas."
                },
                status=400,
            )
        if academic_unit.careers.exists():
            return Response(
                {
                    "detail": "No se puede eliminar una unidad académica que tiene carreras asociadas."
                },
                status=400,
            )
        return super().destroy(request, *args, **kwargs)


class CampusSerializer(serializers.ModelSerializer):
    academic_unit_name = serializers.CharField(
        source="academic_unit.name", read_only=True
    )

    class Meta:
        model = Campus
        fields = [
            "id",
            "code",
            "name",
            "academic_unit",
            "academic_unit_name",
            "is_active",
        ]


class CampusViewSet(viewsets.ModelViewSet):
    queryset = Campus.objects.select_related("academic_unit").all()
    serializer_class = CampusSerializer
    permission_classes = [IsAuthenticated]


class CareerSerializer(serializers.ModelSerializer):
    academic_unit_name = serializers.CharField(
        source="academic_unit.name", read_only=True
    )
    campus_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Career
        fields = [
            "id",
            "code",
            "short_name",
            "name",
            "academic_unit",
            "academic_unit_name",
            "campuses",
            "campus_count",
            "is_active",
        ]


class CareerViewSet(viewsets.ModelViewSet):
    queryset = Career.objects.prefetch_related("campuses").select_related(
        "academic_unit"
    ).annotate(campus_count=Count("campuses"))
    serializer_class = CareerSerializer
    permission_classes = [IsAuthenticated]


router = DefaultRouter()
router.register("universities", UniversityViewSet, basename="university")
router.register("academic-units", AcademicUnitViewSet, basename="academic-unit")
router.register("campuses", CampusViewSet, basename="campus")
router.register("careers", CareerViewSet, basename="career")


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
