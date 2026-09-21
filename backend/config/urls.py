import json

from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.db.models.signals import post_delete, post_save
from django.core.cache import cache
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
    Nomenclador,
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
    queryset = Campus.objects.select_related("academic_unit")
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
    queryset = StudyPlan.objects.select_related("career")
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

    def validate(self, attrs):
        name = attrs.get("name", getattr(self.instance, "name", None))
        study_plan = attrs.get(
            "study_plan", getattr(self.instance, "study_plan", None)
        )
        if name and study_plan:
            qs = StudyArea.objects.filter(
                study_plan=study_plan, name=name
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"name": "Ya existe un área con ese nombre en el plan de estudios."}
                )
        return attrs


class StudyAreaViewSet(viewsets.ModelViewSet):
    queryset = StudyArea.objects.select_related("study_plan__career")
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
    nomenclador_label = serializers.SerializerMethodField()

    def get_nomenclador_label(self, obj):
        if not obj.nomenclador_id:
            return None
        n = obj.nomenclador
        base = f"{n.discipline} / {n.subdiscipline} / {n.specialty}"
        if obj.nomenclador_extra:
            return f"{base} ({obj.nomenclador_extra})"
        return base

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
            "nomenclador",
            "nomenclador_extra",
            "nomenclador_label",
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

        code = attrs.get("code", getattr(self.instance, "code", None))
        if code and Subject.objects.filter(code=code).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError(
                {"code": "Ya existe una materia con ese código."}
            )
        return attrs


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.select_related(
        "study_area__study_plan__career", "nomenclador"
    )
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


def _nomenclador_code(value):
    """Extrae el código del prefijo 'NN - texto' de un valor del nomenclador."""
    if not value:
        return None
    text = str(value).strip()
    if " - " in text:
        return text.split(" - ", 1)[0].strip()
    return text


class NomencladorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nomenclador
        fields = [
            "id",
            "discipline",
            "subdiscipline",
            "specialty",
            "is_active",
        ]

    def validate(self, attrs):
        combo = (
            attrs.get("discipline", getattr(self.instance, "discipline", None)),
            attrs.get("subdiscipline", getattr(self.instance, "subdiscipline", None)),
            attrs.get("specialty", getattr(self.instance, "specialty", None)),
        )
        if all(combo):
            qs = Nomenclador.objects.filter(
                discipline=combo[0],
                subdiscipline=combo[1],
                specialty=combo[2],
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Ya existe un nomenclador con esa disciplina, subdisciplina y especialidad."
                )
            codes = (
                _nomenclador_code(combo[0]),
                _nomenclador_code(combo[1]),
                _nomenclador_code(combo[2]),
            )
            if all(codes):
                candidates = Nomenclador.objects.values(
                    "id", "discipline", "subdiscipline", "specialty"
                )
                if self.instance:
                    candidates = candidates.exclude(pk=self.instance.pk)
                for candidate in candidates:
                    candidate_codes = (
                        _nomenclador_code(candidate["discipline"]),
                        _nomenclador_code(candidate["subdiscipline"]),
                        _nomenclador_code(candidate["specialty"]),
                    )
                    if candidate_codes == codes:
                        raise serializers.ValidationError(
                            "Ya existe un nomenclador con esos códigos de "
                            "disciplina, subdisciplina y especialidad."
                        )
        return attrs


class NomencladorViewSet(viewsets.ModelViewSet):
    queryset = Nomenclador.objects.all()
    serializer_class = NomencladorSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        nomenclador = self.get_object()
        if nomenclador.subjects.exists():
            return Response(
                {
                    "detail": "No se puede eliminar un nomenclador que está asociado a materias."
                },
                status=400,
            )
        return super().destroy(request, *args, **kwargs)


class FormOptionsSerializer(serializers.Serializer):
    universities = UniversitySerializer(many=True, read_only=True)
    academic_units = AcademicUnitSerializer(many=True, read_only=True)
    campuses = CampusSerializer(many=True, read_only=True)
    careers = CareerSerializer(many=True, read_only=True)
    study_plans = StudyPlanSerializer(many=True, read_only=True)
    study_areas = StudyAreaSerializer(many=True, read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)
    nomencladores = NomencladorSerializer(many=True, read_only=True)


FORM_OPTIONS_CACHE_KEY = "api:form_options"


def invalidate_form_options_cache(sender, **kwargs):
    cache.delete(FORM_OPTIONS_CACHE_KEY)


class FormOptionsViewSet(viewsets.ReadOnlyModelViewSet):
    """Devuelve todas las opciones de formulario en un solo endpoint.

    Reemplaza los 5-7 requests separados (universidades, unidades,
    sedes, carreras, planes, áreas, nomencladores) que hacían Carreras,
    Planes, Áreas y Materias al montar, reduciendo a una sola petición
    con prefetch/select_related apropiado.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FormOptionsSerializer

    def list(self, request, *args, **kwargs):
        data = cache.get(FORM_OPTIONS_CACHE_KEY)
        if data is None:
            universities = University.objects.annotate(
                academic_unit_count=Count("academic_units")
            ).filter(is_active=True).order_by("name")
            academic_units = AcademicUnit.objects.select_related(
                "university"
            ).annotate(campus_count=Count("campuses")).filter(
                is_active=True
            ).order_by("code")
            campuses = Campus.objects.select_related("academic_unit").filter(
                is_active=True
            ).order_by("code")
            careers = Career.objects.select_related(
                "academic_unit"
            ).prefetch_related(
                "campuses"
            ).annotate(campus_count=Count("campuses")).filter(
                is_active=True
            ).order_by("code")
            study_plans = StudyPlan.objects.select_related("career").filter(
                is_active=True
            ).order_by("code")
            study_areas = StudyArea.objects.select_related(
                "study_plan__career"
            ).filter(is_active=True).order_by("name")
            subjects = Subject.objects.select_related(
                "study_area__study_plan__career", "nomenclador"
            ).filter(is_active=True).order_by("code")
            nomencladores = Nomenclador.objects.filter(
                is_active=True
            ).order_by("discipline", "subdiscipline", "specialty")

            data = {
                "universities": UniversitySerializer(
                    universities, many=True
                ).data,
                "academic_units": AcademicUnitSerializer(
                    academic_units, many=True
                ).data,
                "campuses": CampusSerializer(campuses, many=True).data,
                "careers": CareerSerializer(careers, many=True).data,
                "study_plans": StudyPlanSerializer(
                    study_plans, many=True
                ).data,
                "study_areas": StudyAreaSerializer(
                    study_areas, many=True
                ).data,
                "subjects": SubjectSerializer(
                    subjects, many=True
                ).data,
                "nomencladores": NomencladorSerializer(
                    nomencladores, many=True
                ).data,
            }
            cache.set(FORM_OPTIONS_CACHE_KEY, data, 5 * 60)
        return Response(data)


_FORM_OPTIONS_MODELS = (
    University,
    AcademicUnit,
    Campus,
    Career,
    StudyPlan,
    StudyArea,
    Subject,
    Nomenclador,
)
for _model in _FORM_OPTIONS_MODELS:
    post_save.connect(
        invalidate_form_options_cache,
        sender=_model,
        weak=False,
        dispatch_uid=f"fo_inv_save_{_model.__name__}",
    )
    post_delete.connect(
        invalidate_form_options_cache,
        sender=_model,
        weak=False,
        dispatch_uid=f"fo_inv_del_{_model.__name__}",
    )


router = DefaultRouter()
router.register("universities", UniversityViewSet, basename="university")
router.register("academic-units", AcademicUnitViewSet, basename="academic-unit")
router.register("campuses", CampusViewSet, basename="campus")
router.register("careers", CareerViewSet, basename="career")
router.register("study-plans", StudyPlanViewSet, basename="study-plan")
router.register("study-areas", StudyAreaViewSet, basename="study-area")
router.register("subjects", SubjectViewSet, basename="subject")
router.register("nomencladores", NomencladorViewSet, basename="nomenclador")
router.register("form-options", FormOptionsViewSet, basename="form-options")


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
