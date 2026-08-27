from django.test import TestCase
from .models import AcademicUnit, University


class UniversityModelTests(TestCase):
    def test_university_short_name_and_active(self):
        university = University.objects.create(
            name="Universidad Nacional de Cuyo",
            short_name="UNCUYO",
            is_active=True,
        )
        self.assertEqual(university.short_name, "UNCUYO")
        self.assertTrue(university.is_active)
        self.assertEqual(str(university), "Universidad Nacional de Cuyo")


class AcademicUnitModelTests(TestCase):
    def test_unit_belongs_to_university(self):
        university = University.objects.create(name="Universidad")
        unit = AcademicUnit.objects.create(code="FAC-01", short_name="Ingeniería", name="Facultad de Ingeniería", university=university)
        self.assertEqual(str(unit), "FAC-01 - Facultad de Ingeniería")
