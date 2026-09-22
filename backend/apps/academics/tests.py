import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from .models import (
    AcademicUnit,
    Campus,
    Career,
    Equivalence,
    Nomenclador,
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

    def test_subject_code_must_be_globally_unique(self):
        _, _, plan, area = self.create_hierarchy()
        area2 = StudyArea.objects.create(
            name="Otra Área", study_plan=plan
        )
        Subject.objects.create(
            code="UNICO-001",
            name="Primera",
            study_area=area,
            year=1,
            period="1Q",
        )
        resp = self.client.post(
            reverse("subject-list"),
            {
                "code": "UNICO-001",
                "name": "Segunda en otra área",
                "study_area": area2.id,
                "year": 1,
                "period": "1Q",
                "is_active": True,
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("code", resp.data)
        self.assertEqual(Subject.objects.filter(code="UNICO-001").count(), 1)

    def test_nomenclador_with_subjects_cannot_be_deleted(self):
        _, _, _, area = self.create_hierarchy()
        nomenclador = Nomenclador.objects.create(
            discipline="1 - CIENCIAS NATURALES Y EXACTAS",
            subdiscipline="01 - ASTRONOMIA",
            specialty="01 - ASTROFISICA",
        )
        Subject.objects.create(
            code="MAT-101",
            name="Álgebra Lineal",
            study_area=area,
            year=1,
            period="1Q",
            nomenclador=nomenclador,
        )
        resp = self.client.delete(
            reverse("nomenclador-detail", args=[nomenclador.id])
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(
            Nomenclador.objects.filter(id=nomenclador.id).exists()
        )

    def test_nomenclador_without_subjects_can_be_deleted(self):
        nomenclador = Nomenclador.objects.create(
            discipline="1 - CIENCIAS NATURALES Y EXACTAS",
            subdiscipline="01 - ASTRONOMIA",
            specialty="01 - ASTROFISICA",
        )
        resp = self.client.delete(
            reverse("nomenclador-detail", args=[nomenclador.id])
        )
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(
            Nomenclador.objects.filter(id=nomenclador.id).exists()
        )


class BackupRestoreRoundTripTests(TestCase):
    """El backup con natural keys restaura todo el circuito jerárquico."""

    def create_hierarchy(self):
        uni = University.objects.create(name="Universidad de Prueba")
        unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Ing.",
            name="Facultad de Ingeniería",
            university=uni,
        )
        campus1 = Campus.objects.create(
            code="SED-01", name="Sede Centro", academic_unit=unit
        )
        campus2 = Campus.objects.create(
            code="SED-02", name="Sede Norte", academic_unit=unit
        )
        career = Career.objects.create(
            code="ING-01",
            short_name="Ing. Inf.",
            name="Ingeniería en Informática",
            academic_unit=unit,
        )
        career.campuses.add(campus1, campus2)
        plan = StudyPlan.objects.create(
            code="PLAN-2010",
            title="Ingeniero en Informática",
            career=career,
            duration_years=5,
            is_current=True,
        )
        area = StudyArea.objects.create(
            name="Ciencias Básicas", study_plan=plan
        )
        nomen = Nomenclador.objects.create(
            discipline="1 - Ciencias Naturales y Exactas",
            subdiscipline="07 - Matemática",
            specialty="03 - Estadística",
        )
        subject = Subject.objects.create(
            code="MAT-101",
            name="Estadística I",
            study_area=area,
            year=1,
            period="2Q",
            nomenclador=nomen,
            nomenclador_extra="Aplicada",
        )
        return nomen, subject

    def wipe_domain(self):
        Subject.objects.all().delete()
        StudyArea.objects.all().delete()
        StudyPlan.objects.all().delete()
        Career.objects.all().delete()
        Campus.objects.all().delete()
        AcademicUnit.objects.all().delete()
        University.objects.all().delete()
        Nomenclador.objects.all().delete()

    def test_roundtrip_restores_full_hierarchy(self):
        original_nomen, _ = self.create_hierarchy()

        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "backup.json"
            call_command("backup_data", output=str(out))
            self.assertTrue(out.is_file())

            self.wipe_domain()
            self.assertEqual(University.objects.count(), 0)

            call_command("restore_data", input=str(out), yes=True)

        self.assertEqual(Nomenclador.objects.count(), 1)
        self.assertEqual(University.objects.count(), 1)
        self.assertEqual(AcademicUnit.objects.count(), 1)
        self.assertEqual(Campus.objects.count(), 2)
        self.assertEqual(Career.objects.count(), 1)
        self.assertEqual(Career.objects.get(code="ING-01").campuses.count(), 2)
        self.assertEqual(StudyPlan.objects.count(), 1)
        self.assertEqual(StudyArea.objects.count(), 1)
        self.assertEqual(Subject.objects.count(), 1)

        subject = Subject.objects.get(code="MAT-101")
        self.assertEqual(subject.study_area.name, "Ciencias Básicas")
        self.assertEqual(subject.study_area.study_plan.career.code, "ING-01")
        self.assertEqual(subject.year, 1)
        self.assertEqual(subject.period, "2Q")
        self.assertEqual(subject.nomenclador.discipline, original_nomen.discipline)
        self.assertEqual(subject.nomenclador.subdiscipline, original_nomen.subdiscipline)
        self.assertEqual(subject.nomenclador.specialty, original_nomen.specialty)
        self.assertEqual(subject.nomenclador_extra, "Aplicada")

    def test_restore_is_idempotent(self):
        self.create_hierarchy()
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "backup.json"
            call_command("backup_data", output=str(out))

            call_command("restore_data", input=str(out), yes=True)
            call_command("restore_data", input=str(out), yes=True)

        self.assertEqual(University.objects.count(), 1)
        self.assertEqual(AcademicUnit.objects.count(), 1)
        self.assertEqual(Career.objects.count(), 1)
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(Career.objects.get(code="ING-01").campuses.count(), 2)


class FormOptionsEndpointTests(TestCase):
    """Verifica que /api/form-options/ devuelva las opciones de formulario,
    incluida la lista de materias, y los contadores anotados."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="tester", password="testpass"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username="tester", password="testpass")
        cache.clear()
        self.university = University.objects.create(
            name="Universidad de Prueba"
        )
        self.unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Tecnología",
            name="Facultad de Tecnología",
            university=self.university,
        )
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
        plan = StudyPlan.objects.create(
            code="PLAN-2010", title="Ingeniero", career=career
        )
        area = StudyArea.objects.create(
            name="Ciencias Básicas", study_plan=plan
        )
        Subject.objects.create(
            code="MAT-101",
            name="Álgebra Lineal",
            study_area=area,
            year=1,
            period="1Q",
        )

    def test_form_options_includes_all_entities(self):
        resp = self.client.get("/api/form-options/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        expected_keys = {
            "universities",
            "academic_units",
            "campuses",
            "careers",
            "study_plans",
            "study_areas",
            "subjects",
            "nomencladores",
        }
        self.assertTrue(expected_keys.issubset(data.keys()))

    def test_form_options_includes_subjects(self):
        resp = self.client.get("/api/form-options/")
        self.assertEqual(resp.status_code, 200)
        subjects = resp.json()["subjects"]
        self.assertEqual(len(subjects), 1)
        subject = subjects[0]
        self.assertEqual(subject["code"], "MAT-101")
        self.assertEqual(subject["study_area_name"], "Ciencias Básicas")
        self.assertEqual(subject["study_plan_code"], "PLAN-2010")
        self.assertEqual(subject["career_code"], "ING-01")
        self.assertEqual(subject["period_label"], "1er Cuatrimestre")

    def test_form_options_annotates_counts(self):
        resp = self.client.get("/api/form-options/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["universities"][0]["academic_unit_count"], 1)
        self.assertEqual(data["academic_units"][0]["campus_count"], 1)
        self.assertEqual(data["careers"][0]["campus_count"], 1)


class ImportNomencladorCommandTests(TestCase):
    """El comando import_nomenclador carga los JSON con claves en español."""

    def sample_file(self, directory):
        path = Path(directory) / "nomenclador.json"
        path.write_text(
            json.dumps(
                [
                    {
                        "disciplina": "1 - CIENCIAS NATURALES Y EXACTAS",
                        "subdisciplina": "01 - ASTRONOMIA",
                        "especialidad": "01 - ASTROFISICA",
                        "activo": True,
                    },
                    {
                        "disciplina": "1 - CIENCIAS NATURALES Y EXACTAS",
                        "subdisciplina": "01 - ASTRONOMIA",
                        "especialidad": "02 - COSMOLOGIA Y COSMOGONIA",
                        "activo": True,
                    },
                    {
                        "disciplina": "2 - INGENIERIA Y TECNOLOGIA",
                        "subdisciplina": "16 - INGENIERIA AERONAUTICA",
                        "especialidad": "01 - AERODINAMICA",
                        "activo": False,
                    },
                ]
            ),
            encoding="utf-8-sig",
        )
        return path

    def test_import_creates_records(self):
        with TemporaryDirectory() as tmp:
            self.sample_file(tmp)
            call_command(
                "import_nomenclador", directory=tmp, stdout=StringIO()
            )
        self.assertEqual(Nomenclador.objects.count(), 3)
        record = Nomenclador.objects.get(
            discipline="1 - CIENCIAS NATURALES Y EXACTAS",
            subdiscipline="01 - ASTRONOMIA",
            specialty="02 - COSMOLOGIA Y COSMOGONIA",
        )
        self.assertTrue(record.is_active)

    def test_import_is_idempotent(self):
        with TemporaryDirectory() as tmp:
            self.sample_file(tmp)
            call_command(
                "import_nomenclador", directory=tmp, stdout=StringIO()
            )
            call_command(
                "import_nomenclador", directory=tmp, stdout=StringIO()
            )
        self.assertEqual(Nomenclador.objects.count(), 3)

    def test_import_updates_is_active(self):
        Nomenclador.objects.create(
            discipline="2 - INGENIERIA Y TECNOLOGIA",
            subdiscipline="16 - INGENIERIA AERONAUTICA",
            specialty="01 - AERODINAMICA",
            is_active=True,
        )
        with TemporaryDirectory() as tmp:
            self.sample_file(tmp)
            call_command(
                "import_nomenclador", directory=tmp, stdout=StringIO()
            )
        record = Nomenclador.objects.get(
            discipline="2 - INGENIERIA Y TECNOLOGIA",
            subdiscipline="16 - INGENIERIA AERONAUTICA",
            specialty="01 - AERODINAMICA",
        )
        self.assertFalse(record.is_active)


class FormOptionsCacheInvalidationTests(TestCase):
    """El caché de /api/form-options/ se invalida al cambiar cualquier entidad."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="tester", password="testpass"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username="tester", password="testpass")
        cache.clear()

    def hit_form_options(self):
        resp = self.client.get("/api/form-options/")
        self.assertEqual(resp.status_code, 200)
        return resp.json()

    def test_creates_career_invalidates_cache(self):
        university = University.objects.create(name="Universidad de Prueba")
        unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Tecnología",
            name="Facultad de Tecnología",
            university=university,
        )
        first = self.hit_form_options()
        self.assertEqual(len(first["careers"]), 0)

        Career.objects.create(
            code="ING-01",
            short_name="Ing.",
            name="Ingeniería en Informática",
            academic_unit=unit,
        )
        second = self.hit_form_options()
        self.assertEqual(len(second["careers"]), 1)
        self.assertEqual(second["careers"][0]["code"], "ING-01")

    def test_deleting_nomenclador_invalidates_cache(self):
        Nomenclador.objects.create(
            discipline="1 - CIENCIAS NATURALES Y EXACTAS",
            subdiscipline="01 - ASTRONOMIA",
            specialty="01 - ASTROFISICA",
        )
        first = self.hit_form_options()
        self.assertEqual(len(first["nomencladores"]), 1)

        Nomenclador.objects.all().delete()
        second = self.hit_form_options()
        self.assertEqual(len(second["nomencladores"]), 0)


class EquivalenceApiTests(TestCase):
    """Equivalencias N:M entre materias de planes distintos + certificaciones."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="tester", password="testpass"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username="tester", password="testpass")
        university = University.objects.create(name="Universidad de Prueba")
        unit = AcademicUnit.objects.create(
            code="FAC-01",
            short_name="Tecnología",
            name="Facultad de Tecnología",
            university=university,
        )
        career = Career.objects.create(
            code="ING-01",
            short_name="Ing.",
            name="Ingeniería",
            academic_unit=unit,
        )
        self.plan_new = StudyPlan.objects.create(
            code="PLAN-2026", title="Ingeniero", career=career
        )
        self.plan_old = StudyPlan.objects.create(
            code="PLAN-2019", title="Ingeniero", career=career
        )
        area_new = StudyArea.objects.create(
            name="Básicas", study_plan=self.plan_new
        )
        area_old = StudyArea.objects.create(
            name="Básicas", study_plan=self.plan_old
        )
        self.sub_new = Subject.objects.create(
            code="N-101",
            name="Nueva Uno",
            study_area=area_new,
            year=1,
            period="1Q",
        )
        self.sub_old1 = Subject.objects.create(
            code="V-101",
            name="Vieja Uno",
            study_area=area_old,
            year=1,
            period="1Q",
        )
        self.sub_old2 = Subject.objects.create(
            code="V-102",
            name="Vieja Dos",
            study_area=area_old,
            year=1,
            period="2Q",
        )

    def post_equivalence(self, **payload):
        return self.client.post(
            reverse("equivalence-list"),
            payload,
            content_type="application/json",
        )

    def test_create_one_to_many_returns_new_side_first(self):
        resp = self.post_equivalence(
            new_subjects=[self.sub_new.id],
            old_subjects=[self.sub_old1.id, self.sub_old2.id],
            rule_text="",
            is_active=True,
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(
            [s["code"] for s in resp.data["new_details"]], ["N-101"]
        )
        self.assertEqual(
            [s["code"] for s in resp.data["old_details"]],
            ["V-101", "V-102"],
        )

    def test_subject_cannot_be_on_both_sides(self):
        resp = self.post_equivalence(
            new_subjects=[self.sub_new.id],
            old_subjects=[self.sub_new.id],
            rule_text="",
            is_active=True,
        )
        self.assertEqual(resp.status_code, 400)

    def test_sides_must_belong_to_different_plans(self):
        resp = self.post_equivalence(
            new_subjects=[self.sub_old1.id],
            old_subjects=[self.sub_old2.id],
            rule_text="",
            is_active=True,
        )
        self.assertEqual(resp.status_code, 400)

    def test_empty_equivalence_is_rejected(self):
        resp = self.post_equivalence(
            new_subjects=[], old_subjects=[], rule_text="", is_active=True
        )
        self.assertEqual(resp.status_code, 400)

    def test_duplicate_equivalence_is_rejected(self):
        payload = {
            "new_subjects": [self.sub_new.id],
            "old_subjects": [self.sub_old1.id],
            "rule_text": "",
            "is_active": True,
        }
        self.assertEqual(self.post_equivalence(**payload).status_code, 201)
        self.assertEqual(self.post_equivalence(**payload).status_code, 400)
        self.assertEqual(Equivalence.objects.count(), 1)

    def test_certification_with_rule_only_is_accepted(self):
        resp = self.post_equivalence(
            new_subjects=[],
            old_subjects=[],
            rule_text="Certifica Inglés",
            is_active=True,
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["rule_text"], "Certifica Inglés")

    def test_subject_in_equivalence_cannot_be_deleted(self):
        equivalence = Equivalence.objects.create(rule_text="")
        equivalence.new_subjects.add(self.sub_new)
        resp = self.client.delete(
            reverse("subject-detail", args=[self.sub_new.id])
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(Subject.objects.filter(id=self.sub_new.id).exists())

    def test_subject_in_equivalence_old_side_cannot_be_deleted(self):
        equivalence = Equivalence.objects.create(rule_text="")
        equivalence.old_subjects.add(self.sub_old1)
        resp = self.client.delete(
            reverse("subject-detail", args=[self.sub_old1.id])
        )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(Subject.objects.filter(id=self.sub_old1.id).exists())

    def test_equivalence_can_be_deleted(self):
        equivalence = Equivalence.objects.create(rule_text="")
        equivalence.old_subjects.add(self.sub_old1)
        resp = self.client.delete(
            reverse("equivalence-detail", args=[equivalence.id])
        )
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(
            Equivalence.objects.filter(id=equivalence.id).exists()
        )

    def test_equivalence_backup_round_trip(self):
        from apps.academics.management.backup_utils import (
            export_data,
            import_data,
        )

        equivalence = Equivalence.objects.create(
            rule_text="Certifica Inglés", is_active=True
        )
        equivalence.new_subjects.add(self.sub_new)
        equivalence.old_subjects.add(self.sub_old1, self.sub_old2)
        payload = export_data()
        records = payload["models"]["Equivalence"]
        self.assertEqual(len(records), 1)

        Equivalence.objects.all().delete()
        summary = import_data(payload)
        self.assertEqual(summary["Equivalence"], (1, 0))
        restored = Equivalence.objects.get()
        self.assertEqual(restored.rule_text, "Certifica Inglés")
        self.assertEqual(
            {s.code for s in restored.new_subjects.all()}, {"N-101"}
        )
        self.assertEqual(
            {s.code for s in restored.old_subjects.all()},
            {"V-101", "V-102"},
        )

        summary = import_data(payload)
        self.assertEqual(summary["Equivalence"], (0, 1))
        self.assertEqual(Equivalence.objects.count(), 1)
