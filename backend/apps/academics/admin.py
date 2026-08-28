from django.contrib import admin
from .models import AcademicUnit, Campus, University, Career, StudyArea, StudyPlan


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ["name", "short_name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "short_name"]


@admin.register(AcademicUnit)
class AcademicUnitAdmin(admin.ModelAdmin):
    list_display = ["code", "short_name", "name", "university", "is_active"]
    list_filter = ["is_active", "university"]
    search_fields = ["code", "short_name", "name"]


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "academic_unit", "is_active"]
    list_filter = ["is_active", "academic_unit"]
    search_fields = ["code", "name"]


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ["code", "short_name", "name", "academic_unit", "is_active"]
    list_filter = ["is_active", "academic_unit"]
    search_fields = ["code", "short_name", "name"]
    filter_horizontal = ["campuses"]


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ["code", "title", "career", "is_active", "is_current"]
    list_filter = ["is_active", "is_current", "career"]
    search_fields = ["code", "title"]


@admin.register(StudyArea)
class StudyAreaAdmin(admin.ModelAdmin):
    list_display = ["name", "study_plan", "is_active"]
    list_filter = ["is_active", "study_plan"]
    search_fields = ["name"]
