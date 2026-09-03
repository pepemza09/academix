from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import (
    AcademicUnit,
    Campus,
    Career,
    StudyArea,
    StudyPlan,
    Subject,
    University,
)


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


class SubjectModelTests(TestCase):
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
            duration_years=5,
        )
        self.area = StudyArea.objects.create(
            name="Ciencias Básicas",
            study_plan=self.plan,
        )

    def test_subject_belongs_to_area(self):
        subject = Subject.objects.create(
            code="MAT-101",
            name="Álgebra Lineal",
            study_area=self.area,
            year=1,
            period=Subject.Period.FIRST_QUARTER,
        )
        self.assertEqual(str(subject), "MAT-101 - Álgebra Lineal")
        self.assertEqual(subject.study_area, self.area)
        self.assertEqual(subject.period, "1Q")
        self.assertTrue(subject.is_active)

    def test_subject_with_annual_period(self):
        subject = Subject.objects.create(
            code="MAT-102",
            name="Física I",
            study_area=self.area,
            year=2,
            period=Subject.Period.ANNUAL,
        )
        self.assertEqual(subject.period, "AN")

    def test_study_plan_can_have_duration(self):
        self.assertEqual(self.plan.duration_years, 5)


class DeleteProtectionApiTests(TestCase):
    """Verifica la regla de integridad referencial: no se puede eliminar una
    entidad padre mientras tenga dependencias asociadas (debe devolver 400)."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="tester", password="testpass"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username="tester", password="testpass")
        self.university = University.objects.create(
            name="Universidad de Prueba"
        )
        self.unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Tecnología",
            name="Facultad de Tecnología",
            university=self.university,
        )

    def create_hierarchy(self):
        campus = Campus.objects.create(
            code="SED-01", name="Sede Centro", academic_unit=self.unit
        )
        career = Career.objects.create(
            code="ING-01",
            short_name="Ing.",
            name="Ingeniería",
            academic_unit=self.unit,
        )
        plan = StudyPlan.objects.create(
            code="PLAN-2010", title="Ingeniero", career=career
        )
        area = StudyArea.objects.create(
            name="Ciencias Básicas", study_plan=plan
        )
        return campus, career, plan, area

    def test_university_with_units_cannot_be_deleted(self):
        self.client.delete(reverse("university-detail", args=[self.university.id]))
        self.assertTrue(University.objects.filter(id=self.university.id).exists())

    def test_university_without_units_can_be_deleted(self):
        unit = self.unit
        unit.delete()
        resp = self.client.delete(
            reverse("university-detail", args=[self.university.id])
        )
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(University.objects.filter(id=self.university.id).exists())

    def test_academic_unit_with_campus_cannot_be_deleted(self):
        Campus.objects.create(
            code="SED-01", name="Sede Centro", academic_unit=self.unit
        )
        self.client.delete(reverse("academic-unit-detail", args=[self.unit.id]))
        self.assertTrue(AcademicUnit.objects.filter(id=self.unit.id).exists())

    def test_academic_unit_with_career_cannot_be_deleted(self):
        Career.objects.create(
            code="ING-01",
            short_name="Ing.",
            name="Ingeniería",
            academic_unit=self.unit,
        )
        self.client.delete(reverse("academic-unit-detail", args=[self.unit.id]))
        self.assertTrue(AcademicUnit.objects.filter(id=self.unit.id).exists())

    def test_campus_referenced_by_career_cannot_be_deleted(self):
        campus = Campus.objects.create(
            code="SED-01", name="Sede Centro", academic_unit=self.unit
        )
        career = Career.objects.create(
            code="ING-01",
            short_name="Ing.",
            name="Ingeniería",
            academic_unit=self.unit,
        )
        career.campuses.add(campus)
        resp = self.client.delete(reverse("campus-detail", args=[campus.id]))
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(Campus.objects.filter(id=campus.id).exists())

    def test_campus_not_referenced_by_career_can_be_deleted(self):
        campus = self.create_hierarchy()[0]
        campus.careers.clear()
        resp = self.client.delete(reverse("campus-detail", args=[campus.id]))
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Campus.objects.filter(id=campus.id).exists())

    def test_career_with_plans_cannot_be_deleted(self):
        _, career, _, _ = self.create_hierarchy()
        self.client.delete(reverse("career-detail", args=[career.id]))
        self.assertTrue(Career.objects.filter(id=career.id).exists())

    def test_study_plan_with_areas_cannot_be_deleted(self):
        _, _, plan, _ = self.create_hierarchy()
        self.client.delete(reverse("study-plan-detail", args=[plan.id]))
        self.assertTrue(StudyPlan.objects.filter(id=plan.id).exists())

    def test_study_area_can_be_deleted(self):
        _, _, _, area = self.create_hierarchy()
        resp = self.client.delete(reverse("study-area-detail", args=[area.id]))
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(StudyArea.objects.filter(id=area.id).exists())

    def test_study_area_with_subjects_cannot_be_deleted(self):
        _, _, _, area = self.create_hierarchy()
        Subject.objects.create(
            code="MAT-101",
            name="Álgebra Lineal",
            study_area=area,
            year=1,
            period="1Q",
        )
        resp = self.client.delete(reverse("study-area-detail", args=[area.id]))
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(StudyArea.objects.filter(id=area.id).exists())

    def test_subject_can_be_created_and_deleted(self):
        _, _, plan, area = self.create_hierarchy()
        creation = self.client.post(
            reverse("subject-list"),
            {
                "code": "MAT-101",
                "name": "Álgebra Lineal",
                "study_area": area.id,
                "year": 1,
                "period": "1Q",
                "is_active": True,
            },
            content_type="application/json",
        )
        self.assertEqual(creation.status_code, 201)
        subject_id = creation.data["id"]
        self.assertEqual(creation.data["year"], 1)
        self.assertEqual(creation.data["period_label"], "1er Cuatrimestre")
        self.assertEqual(creation.data["duration_years"], plan.duration_years)
        resp = self.client.delete(reverse("subject-detail", args=[subject_id]))
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Subject.objects.filter(id=subject_id).exists())

    def test_subject_year_cannot_exceed_plan_duration(self):
        _, _, _, area = self.create_hierarchy()
        resp = self.client.post(
            reverse("subject-list"),
            {
                "code": "MAT-999",
                "name": "Materia Invalida",
                "study_area": area.id,
                "year": 99,
                "period": "1Q",
                "is_active": True,
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("year", resp.data)
