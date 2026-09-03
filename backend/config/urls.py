from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.core.files.images import get_image_dimensions
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from apps.academics.models import (
    AcademicUnit,
    Campus,
    Career,
    StudyArea,
    StudyPlan,
    Subject,
    University,
)
from apps.users.models import Profile


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

    def destroy(self, request, *args, **kwargs):
        campus = self.get_object()
        if campus.careers.exists():
            return Response(
                {
                    "detail": "No se puede eliminar una sede que está asociada a carreras."
                },
                status=400,
            )
        return super().destroy(request, *args, **kwargs)


class CareerSerializer(serializers.ModelSerializer):
    academic_unit_name = serializers.CharField(
        source="academic_unit.name", read_only=True
    )
    campus_count = serializers.IntegerField(read_only=True)
    campus_details = serializers.SerializerMethodField()

    def get_campus_details(self, obj):
        return [
            {"id": campus.id, "code": campus.code, "name": campus.name}
            for campus in obj.campuses.all()
        ]

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
            "campus_details",
            "is_active",
        ]


class CareerViewSet(viewsets.ModelViewSet):
    queryset = Career.objects.prefetch_related("campuses").select_related(
        "academic_unit"
    ).annotate(campus_count=Count("campuses"))
    serializer_class = CareerSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        career = self.get_object()
        if career.study_plans.exists():
            return Response(
                {
                    "detail": "No se puede eliminar una carrera que tiene planes de estudio asociados."
                },
                status=400,
            )
        return super().destroy(request, *args, **kwargs)


class StudyPlanSerializer(serializers.ModelSerializer):
    career_name = serializers.CharField(source="career.name", read_only=True)
    career_code = serializers.CharField(source="career.code", read_only=True)

    class Meta:
        model = StudyPlan
        fields = [
            "id",
            "code",
            "title",
            "intermediate_title",
            "duration_years",
            "career",
            "career_name",
            "career_code",
            "is_active",
            "is_current",
        ]


class StudyPlanViewSet(viewsets.ModelViewSet):
    queryset = StudyPlan.objects.select_related("career").all()
    serializer_class = StudyPlanSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        study_plan = self.get_object()
        if study_plan.areas.exists():
            return Response(
                {
                    "detail": "No se puede eliminar un plan de estudios que tiene áreas asociadas."
                },
                status=400,
            )
        return super().destroy(request, *args, **kwargs)


class StudyAreaSerializer(serializers.ModelSerializer):
    study_plan_code = serializers.CharField(
        source="study_plan.code", read_only=True
    )
    study_plan_title = serializers.CharField(
        source="study_plan.title", read_only=True
    )
    career_name = serializers.CharField(
        source="study_plan.career.name", read_only=True
    )
    career_code = serializers.CharField(
        source="study_plan.career.code", read_only=True
    )

    class Meta:
        model = StudyArea
        fields = [
            "id",
            "name",
            "study_plan",
            "study_plan_code",
            "study_plan_title",
            "career_name",
            "career_code",
            "is_active",
        ]


class StudyAreaViewSet(viewsets.ModelViewSet):
    queryset = StudyArea.objects.select_related("study_plan__career").all()
    serializer_class = StudyAreaSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        study_area = self.get_object()
        if study_area.subjects.exists():
            return Response(
                {
                    "detail": "No se puede eliminar un área que tiene materias asociadas."
                },
                status=400,
            )
        return super().destroy(request, *args, **kwargs)


class SubjectSerializer(serializers.ModelSerializer):
    period_label = serializers.CharField(
        source="get_period_display", read_only=True
    )
    study_area_name = serializers.CharField(
        source="study_area.name", read_only=True
    )
    study_plan_code = serializers.CharField(
        source="study_area.study_plan.code", read_only=True
    )
    study_plan_title = serializers.CharField(
        source="study_area.study_plan.title", read_only=True
    )
    career_name = serializers.CharField(
        source="study_area.study_plan.career.name", read_only=True
    )
    career_code = serializers.CharField(
        source="study_area.study_plan.career.code", read_only=True
    )
    duration_years = serializers.IntegerField(
        source="study_area.study_plan.duration_years", read_only=True
    )

    class Meta:
        model = Subject
        fields = [
            "id",
            "code",
            "name",
            "year",
            "period",
            "period_label",
            "study_area",
            "study_area_name",
            "study_plan_code",
            "study_plan_title",
            "career_name",
            "career_code",
            "duration_years",
            "is_active",
        ]

    def validate(self, attrs):
        year = attrs.get("year", getattr(self.instance, "year", None))
        study_area = attrs.get(
            "study_area", getattr(self.instance, "study_area", None)
        )
        if year and study_area:
            duration = study_area.study_plan.duration_years
            if year < 1 or year > duration:
                raise serializers.ValidationError(
                    {"year": f"El año debe estar entre 1 y {duration} (duración del plan)."}
                )
        return attrs


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.select_related(
        "study_area__study_plan__career"
    ).all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


router = DefaultRouter()
router.register("universities", UniversityViewSet, basename="university")
router.register("academic-units", AcademicUnitViewSet, basename="academic-unit")
router.register("campuses", CampusViewSet, basename="campus")
router.register("careers", CareerViewSet, basename="career")
router.register("study-plans", StudyPlanViewSet, basename="study-plan")
router.register("study-areas", StudyAreaViewSet, basename="study-area")
router.register("subjects", SubjectViewSet, basename="subject")


@require_http_methods(["GET"])
def health(request):
    return JsonResponse({"status": "ok", "service": "academix-api"})


def user_payload(user):
    is_local = not user.social_auth.exists()
    profile = Profile.objects.filter(user=user).only("avatar").first()
    avatar = profile.avatar.url if profile and profile.avatar else None
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_local": is_local,
        "auth_provider": "local" if is_local else "google",
        "avatar": avatar,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


@require_http_methods(["POST"])
@ensure_csrf_cookie
def login_view(request):
    import json
    payload = json.loads(request.body or "{}")
    user = authenticate(request, username=payload.get("username"), password=payload.get("password"))
    if user is None:
        return JsonResponse({"detail": "Credenciales inválidas."}, status=401)
    login(request, user)
    return JsonResponse(user_payload(user))


@ensure_csrf_cookie
def me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Autenticación requerida."}, status=401)
    return JsonResponse(user_payload(request.user))


@require_http_methods(["POST"])
@ensure_csrf_cookie
def upload_avatar_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Autenticación requerida."}, status=401)

    avatar = request.FILES.get("avatar")
    if avatar is None:
        return JsonResponse({"detail": "Debes adjuntar una imagen."}, status=400)

    if avatar.size > 5 * 1024 * 1024:
        return JsonResponse(
            {"detail": "La imagen no debe superar los 5 MB."}, status=400
        )

    try:
        width, height = get_image_dimensions(avatar)
    except Exception:
        width = height = None

    if not width or not height:
        return JsonResponse(
            {"detail": "El archivo debe ser una imagen válida."}, status=400
        )

    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.avatar = avatar
    profile.save(update_fields=["avatar", "updated_at"])

    return JsonResponse(
        {"status": "ok", "detail": "Foto de perfil actualizada.", "avatar": profile.avatar.url}
    )


@require_http_methods(["POST"])
@ensure_csrf_cookie
def change_password_view(request):
    import json

    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Autenticación requerida."}, status=401)

    if request.user.social_auth.exists():
        return JsonResponse(
            {
                "detail": "Los usuarios autenticados con Google no pueden cambiar su contraseña."
            },
            status=400,
        )

    payload = json.loads(request.body or "{}")
    current_password = payload.get("current_password")
    new_password = payload.get("new_password")

    if not request.user.check_password(current_password or ""):
        return JsonResponse(
            {"detail": "La contraseña actual es incorrecta."}, status=400
        )

    if not new_password or len(new_password) < 8:
        return JsonResponse(
            {"detail": "La nueva contraseña debe tener al menos 8 caracteres."},
            status=400,
        )

    request.user.set_password(new_password)
    request.user.save(update_fields=["password"])
    return JsonResponse({"status": "ok", "detail": "Contraseña actualizada."})


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
    path("api/auth/change-password/", change_password_view),
    path("api/auth/upload-avatar/", upload_avatar_view),
    path("api/auth/logout/", logout_view),
    path("auth/", include("social_django.urls", namespace="social")),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    from django.urls import re_path
    from django.views.static import serve as media_serve

    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            media_serve,
            {"document_root": settings.MEDIA_ROOT},
            name="media",
        )
    ]
