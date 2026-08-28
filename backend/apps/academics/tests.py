from django.test import TestCase
from .models import AcademicUnit, Campus, University


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
        self.assertEqual(unit.university, university)


class UniversityProtectionTests(TestCase):
    def test_cannot_delete_university_with_units(self):
        university = University.objects.create(name="Universidad")
        AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Ingeniería",
            name="Facultad de Ingeniería",
            university=university,
        )
        self.assertTrue(university.academic_units.exists())


class CampusModelTests(TestCase):
    def test_campus_belongs_to_academic_unit(self):
        university = University.objects.create(name="Universidad")
        unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Ingeniería",
            name="Facultad de Ingeniería",
            university=university,
        )
        campus = Campus.objects.create(
            code="SED-01",
            name="Sede Centro",
            academic_unit=unit,
        )
        self.assertEqual(str(campus), "SED-01 - Sede Centro")
        self.assertEqual(campus.academic_unit, unit)


class AcademicUnitProtectionTests(TestCase):
    def test_university_has_campuses(self):
        university = University.objects.create(name="Universidad")
        unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Ingeniería",
            name="Facultad de Ingeniería",
            university=university,
        )
        Campus.objects.create(
            code="SED-01",
            name="Sede Centro",
            academic_unit=unit,
        )
        self.assertTrue(unit.campuses.exists())
