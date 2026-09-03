from django.test import TestCase
from .models import AcademicUnit, Campus, Career, StudyArea, StudyPlan, University


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


class StudyPlanModelTests(TestCase):
    def setUp(self):
        self.university = University.objects.create(name="Universidad")
        self.unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Ingeniería",
            name="Facultad de Ingeniería",
            university=self.university,
        )
        self.career = Career.objects.create(
            code="ING-01",
            short_name="Ing. Informática",
            name="Ingeniería en Informática",
            academic_unit=self.unit,
        )

    def test_study_plan_belongs_to_career(self):
        plan = StudyPlan.objects.create(
            code="PLAN-2010",
            title="Ingeniero en Informática",
            career=self.career,
            is_active=True,
            is_current=True,
        )
        self.assertEqual(str(plan), "PLAN-2010 - Ingeniero en Informática")
        self.assertEqual(plan.career, self.career)
        self.assertTrue(plan.is_active)
        self.assertTrue(plan.is_current)

    def test_study_plan_can_be_inactive_and_not_current(self):
        plan = StudyPlan.objects.create(
            code="PLAN-2000",
            title="Ingeniero en Informática (Plan viejo)",
            career=self.career,
            is_active=False,
            is_current=False,
        )
        self.assertFalse(plan.is_active)
        self.assertFalse(plan.is_current)

    def test_study_plan_can_have_intermediate_title(self):
        plan = StudyPlan.objects.create(
            code="PLAN-2010",
            title="Ingeniero en Informática",
            intermediate_title="Técnico Universitario en Programación",
            career=self.career,
        )
        self.assertEqual(
            plan.intermediate_title,
            "Técnico Universitario en Programación",
        )

    def test_study_plan_intermediate_title_defaults_to_empty(self):
        plan = StudyPlan.objects.create(
            code="PLAN-2010",
            title="Ingeniero en Informática",
            career=self.career,
        )
        self.assertEqual(plan.intermediate_title, "")


class StudyPlanProtectionTests(TestCase):
    def test_career_with_study_plans_cannot_be_deleted(self):
        university = University.objects.create(name="Universidad")
        unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Ingeniería",
            name="Facultad de Ingeniería",
            university=university,
        )
        career = Career.objects.create(
            code="ING-01",
            short_name="Ing. Informática",
            name="Ingeniería en Informática",
            academic_unit=unit,
        )
        StudyPlan.objects.create(
            code="PLAN-2010",
            title="Ingeniero en Informática",
            career=career,
        )
        self.assertTrue(career.study_plans.exists())


class StudyAreaModelTests(TestCase):
    def setUp(self):
        self.university = University.objects.create(name="Universidad")
        self.unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Ingeniería",
            name="Facultad de Ingeniería",
            university=self.university,
        )
        self.career = Career.objects.create(
            code="ING-01",
            short_name="Ing. Informática",
            name="Ingeniería en Informática",
            academic_unit=self.unit,
        )
        self.plan = StudyPlan.objects.create(
            code="PLAN-2010",
            title="Ingeniero en Informática",
            career=self.career,
        )

    def test_area_belongs_to_study_plan(self):
        area = StudyArea.objects.create(
            name="Ciencias Básicas",
            study_plan=self.plan,
            is_active=True,
        )
        self.assertEqual(str(area), "Ciencias Básicas")
        self.assertEqual(area.study_plan, self.plan)
        self.assertTrue(area.is_active)

    def test_area_can_be_inactive(self):
        area = StudyArea.objects.create(
            name="Ciencias de la Computación",
            study_plan=self.plan,
            is_active=False,
        )
        self.assertFalse(area.is_active)


class StudyAreaProtectionTests(TestCase):
    def test_study_plan_with_areas_cannot_be_deleted(self):
        university = University.objects.create(name="Universidad")
        unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Ingeniería",
            name="Facultad de Ingeniería",
            university=university,
        )
        career = Career.objects.create(
            code="ING-01",
            short_name="Ing. Informática",
            name="Ingeniería en Informática",
            academic_unit=unit,
        )
        plan = StudyPlan.objects.create(
            code="PLAN-2010",
            title="Ingeniero en Informática",
            career=career,
        )
        StudyArea.objects.create(
            name="Ciencias Básicas",
            study_plan=plan,
        )
        self.assertTrue(plan.areas.exists())
        self.assertTrue(career.study_plans.exists())
