from django.contrib import admin
from .models import AcademicUnit, University


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
