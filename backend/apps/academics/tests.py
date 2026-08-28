from django.test import TestCase
from .models import AcademicUnit, Campus, Career, University


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


class CareerModelTests(TestCase):
    def setUp(self):
        self.university = University.objects.create(name="Universidad")
        self.unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Ingeniería",
            name="Facultad de Ingeniería",
            university=self.university,
        )
        self.campus = Campus.objects.create(
            code="SED-01",
            name="Sede Centro",
            academic_unit=self.unit,
        )

    def test_career_belongs_to_academic_unit(self):
        career = Career.objects.create(
            code="ING-01",
            short_name="Ing. Informática",
            name="Ingeniería en Informática",
            academic_unit=self.unit,
        )
        career.campuses.add(self.campus)
        self.assertEqual(str(career), "ING-01 - Ingeniería en Informática")
        self.assertEqual(career.academic_unit, self.unit)
        self.assertEqual(career.campuses.count(), 1)

    def test_career_can_be_in_multiple_campuses(self):
        campus2 = Campus.objects.create(
            code="SED-02",
            name="Sede Godoy Cruz",
            academic_unit=self.unit,
        )
        career = Career.objects.create(
            code="ING-01",
            short_name="Ing. Informática",
            name="Ingeniería en Informática",
            academic_unit=self.unit,
        )
        career.campuses.add(self.campus, campus2)
        self.assertEqual(career.campuses.count(), 2)


class CareerProtectionTests(TestCase):
    def test_academic_unit_with_careers_cannot_be_deleted_via_view(self):
        university = University.objects.create(name="Universidad")
        unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Ingeniería",
            name="Facultad de Ingeniería",
            university=university,
        )
        Career.objects.create(
            code="ING-01",
            short_name="Ing. Informática",
            name="Ingeniería en Informática",
            academic_unit=unit,
        )
        self.assertTrue(unit.careers.exists())
