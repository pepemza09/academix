import { useCallback, useEffect, useState } from "react";
import PageMeta from "../../components/common/PageMeta";
import PageBreadcrumb from "../../components/common/PageBreadCrumb";
import Button from "../../components/ui/button/Button";
import { Modal } from "../../components/ui/modal";
import Input from "../../components/form/input/InputField";
import Combobox from "../../components/form/Combobox";
import Label from "../../components/form/Label";
import Badge from "../../components/ui/badge/Badge";
import Switch from "../../components/form/switch/Switch";
import { PencilIcon, TrashBinIcon } from "../../icons";
import {
  PERIOD_OPTIONS,
  Subject,
  SubjectPayload,
  subjectApi,
} from "../../api/subjects";
import { StudyArea, studyAreaApi } from "../../api/studyAreas";
import { StudyPlan, studyPlanApi } from "../../api/studyPlans";
import { Career, careerApi } from "../../api/careers";
import { AcademicUnit, academicUnitApi } from "../../api/academicUnits";
import { University, universityApi } from "../../api/universities";

type SubjectForm = SubjectPayload & {
  university: number;
  academic_unit: number;
  career: number;
  study_plan: number;
};

const EMPTY_FORM: SubjectForm = {
  code: "",
  name: "",
  year: 1,
  period: "1Q",
  study_area: 0,
  is_active: true,
  university: 0,
  academic_unit: 0,
  career: 0,
  study_plan: 0,
};

export default function Materias() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [areas, setAreas] = useState<StudyArea[]>([]);
  const [plans, setPlans] = useState<StudyPlan[]>([]);
  const [careers, setCareers] = useState<Career[]>([]);
  const [academicUnits, setAcademicUnits] = useState<AcademicUnit[]>([]);
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Subject | null>(null);
  const [form, setForm] = useState<SubjectForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleteTarget, setDeleteTarget] = useState<Subject | null>(null);
  const [deleting, setDeleting] = useState(false);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "inactive">("all");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [
        subjectsData,
        areasData,
        plansData,
        careersData,
        unitsData,
        universitiesData,
      ] = await Promise.all([
        subjectApi.list(),
        studyAreaApi.list(),
        studyPlanApi.list(),
        careerApi.list(),
        academicUnitApi.list(),
        universityApi.list(),
      ]);
      setSubjects(subjectsData);
      setAreas(areasData);
      setPlans(plansData);
      setCareers(careersData);
      setAcademicUnits(unitsData);
      setUniversities(universitiesData);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "No se pudieron cargar las materias.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const selectedPlan = form.study_plan
    ? plans.find((p) => p.id === form.study_plan)
    : undefined;
  const planDuration = selectedPlan ? selectedPlan.duration_years : 0;

  const universityOptions = universities.map((u) => ({
    value: u.id,
    label: u.short_name ? `${u.name} (${u.short_name})` : u.name,
  }));

  const availableUnits = form.university
    ? academicUnits.filter((u) => u.university === form.university)
    : [];

  const academicUnitOptions = availableUnits.map((u) => ({
    value: u.id,
    label: u.short_name ? `${u.name} (${u.short_name})` : u.name,
  }));

  const availableCareers = form.academic_unit
    ? careers.filter((c) => c.academic_unit === form.academic_unit)
    : [];

  const careerOptions = availableCareers.map((c) => ({
    value: c.id,
    label: c.short_name ? `${c.name} (${c.short_name})` : c.name,
  }));

  const availablePlans = form.career
    ? plans.filter((p) => p.career === form.career)
    : [];

  const planOptions = availablePlans.map((p) => ({
    value: p.id,
    label: `${p.code} - ${p.title}`,
  }));

  const availableAreas = form.study_plan
    ? areas.filter((a) => a.study_plan === form.study_plan)
    : [];

  const areaOptions = availableAreas.map((a) => ({
    value: a.id,
    label: a.name,
  }));

  const filteredSubjects = subjects.filter((subject) => {
    const term = search.trim().toLowerCase();
    const matchesSearch =
      !term ||
      subject.code.toLowerCase().includes(term) ||
      subject.name.toLowerCase().includes(term) ||
      subject.career_name.toLowerCase().includes(term) ||
      subject.career_code.toLowerCase().includes(term) ||
      subject.study_area_name.toLowerCase().includes(term);
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "active" && subject.is_active) ||
      (statusFilter === "inactive" && !subject.is_active);
    return matchesSearch && matchesStatus;
  });

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  };

  const openEdit = (subject: Subject) => {
    const area = areas.find((a) => a.id === subject.study_area);
    const plan = area
      ? plans.find((p) => p.id === area.study_plan)
      : undefined;
    const career = plan
      ? careers.find((c) => c.id === plan.career)
      : undefined;
    const unit = career
      ? academicUnits.find((u) => u.id === career.academic_unit)
      : undefined;
    setEditing(subject);
    setForm({
      code: subject.code,
      name: subject.name,
      year: subject.year,
      period: subject.period,
      study_area: subject.study_area,
      is_active: subject.is_active,
      university: unit ? unit.university : 0,
      academic_unit: career ? career.academic_unit : 0,
      career: plan ? plan.career : 0,
      study_plan: area ? area.study_plan : 0,
    });
    setFormError(null);
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    setFormError(null);
    if (!form.university) {
      setFormError("Debes seleccionar una universidad.");
      return;
    }
    if (!form.academic_unit) {
      setFormError("Debes seleccionar una unidad académica.");
      return;
    }
    if (!form.career) {
      setFormError("Debes seleccionar una carrera.");
      return;
    }
    if (!form.study_plan) {
      setFormError("Debes seleccionar un plan de estudios.");
      return;
    }
    if (!form.study_area) {
      setFormError("Debes seleccionar un área.");
      return;
    }
    if (!form.code.trim() || !form.name.trim()) {
      setFormError("El código y el nombre de la materia son obligatorios.");
      return;
    }
    if (!form.year || form.year < 1 || (planDuration && form.year > planDuration)) {
      setFormError(
        planDuration
          ? `El año debe estar entre 1 y ${planDuration} (duración del plan).`
          : "El año debe ser al menos 1.",
      );
      return;
    }
    setSaving(true);
    try {
      if (editing) {
        const updated = await subjectApi.update(editing.id, form);
        setSubjects((prev) =>
          prev.map((s) => (s.id === updated.id ? updated : s)),
        );
      } else {
        const created = await subjectApi.create(form);
        setSubjects((prev) => [...prev, created]);
      }
      setModalOpen(false);
    } catch (e) {
      setFormError(
        e instanceof Error ? e.message : "No se pudo guardar la materia.",
      );
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await subjectApi.remove(deleteTarget.id);
      setSubjects((prev) => prev.filter((s) => s.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "No se pudo eliminar la materia.",
      );
      setDeleteTarget(null);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div>
      <PageMeta title="Academix" description="Gestión de materias" />
      <PageBreadcrumb pageTitle="Materias" />

      <div className="space-y-6">
        <div className="flex justify-end">
          <Button
            onClick={openCreate}
            size="sm"
            className="font-bold"
            startIcon={
              <svg
                className="h-4 w-4"
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M8 3v10M3 8h10"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            }
          >
            Nueva materia
          </Button>
        </div>

        {error && (
          <div className="rounded-2xl border border-error-200 bg-error-50 px-5 py-4 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
            {error}
          </div>
        )}

        <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
          <div className="border-b border-gray-200 px-5 py-4 dark:border-gray-800">
            <h2 className="font-semibold text-gray-900 dark:text-white">
              Listado de materias
            </h2>
          </div>

          <div className="flex flex-col gap-3 border-b border-gray-200 px-5 py-4 dark:border-gray-800 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar por código, nombre, área o carrera…"
                className="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 pr-10 text-sm shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
              />
              <svg
                className="absolute right-4 top-1/2 size-5 -translate-y-1/2 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M21 21l-4.35-4.35M17 10.5a6.5 6.5 0 11-13 0 6.5 6.5 0 0113 0z"
                />
              </svg>
            </div>
            <div className="w-full sm:w-52">
              <select
                value={statusFilter}
                onChange={(e) =>
                  setStatusFilter(
                    e.target.value as "all" | "active" | "inactive",
                  )
                }
                className="h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800"
              >
                <option value="all" className="bg-white text-gray-800 dark:bg-gray-900 dark:text-white/90">
                  Todas
                </option>
                <option value="active" className="bg-white text-gray-800 dark:bg-gray-900 dark:text-white/90">
                  Solo activas
                </option>
                <option value="inactive" className="bg-white text-gray-800 dark:bg-gray-900 dark:text-white/90">
                  Solo inactivas
                </option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            {loading ? (
              <div className="px-5 py-10 text-center text-sm text-gray-500 dark:text-gray-400">
                Cargando materias…
              </div>
            ) : filteredSubjects.length === 0 ? (
              <div className="px-5 py-10 text-center text-sm text-gray-500 dark:text-gray-400">
                No se encontraron materias con los criterios de búsqueda.
              </div>
            ) : (
              <table className="w-full min-w-[980px] text-left text-sm">
                <thead className="bg-gray-50 text-xs uppercase text-gray-500 dark:bg-white/[0.02] dark:text-gray-400">
                  <tr>
                    <th className="px-5 py-3">Código</th>
                    <th className="px-5 py-3">Nombre</th>
                    <th className="px-5 py-3">Año</th>
                    <th className="px-5 py-3">Período</th>
                    <th className="px-5 py-3">Área</th>
                    <th className="px-5 py-3">Plan</th>
                    <th className="px-5 py-3">Carrera</th>
                    <th className="px-5 py-3">Activa</th>
                    <th className="px-5 py-3 text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {filteredSubjects.map((subject) => (
                    <tr
                      key={subject.id}
                      className="hover:bg-gray-50 dark:hover:bg-white/[0.02]"
                    >
                      <td className="px-5 py-4 font-medium text-gray-900 dark:text-white">
                        {subject.code}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        {subject.name}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        {subject.year}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        {subject.period_label}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        {subject.study_area_name}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        <div className="font-medium text-gray-800 dark:text-white">
                          {subject.study_plan_title}
                        </div>
                        <div className="text-xs text-gray-400 dark:text-gray-500">
                          {subject.study_plan_code}
                        </div>
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        <div className="font-medium text-gray-800 dark:text-white">
                          {subject.career_name}
                        </div>
                        <div className="text-xs text-gray-400 dark:text-gray-500">
                          {subject.career_code}
                        </div>
                      </td>
                      <td className="px-5 py-4">
                        {subject.is_active ? (
                          <Badge color="success">Activa</Badge>
                        ) : (
                          <Badge color="warning">Inactiva</Badge>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => openEdit(subject)}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-gray-100 hover:text-brand-500 dark:text-gray-400 dark:hover:bg-white/5"
                            aria-label={`Editar ${subject.name}`}
                            title="Editar"
                          >
                            <PencilIcon className="size-4" />
                          </button>
                          <button
                            onClick={() => setDeleteTarget(subject)}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-error-50 hover:text-error-500 dark:text-gray-400 dark:hover:bg-error-500/10"
                            aria-label={`Eliminar ${subject.name}`}
                            title="Eliminar"
                          >
                            <TrashBinIcon className="size-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        centered
        className="w-[80vw] max-w-[80vw]"
      >
        <div className="p-6 sm:p-8">
          <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
            {editing ? "Editar materia" : "Nueva materia"}
          </h3>

          {formError && (
            <div className="mb-4 rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
              {formError}
            </div>
          )}

          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="subject-university">Universidad</Label>
                <Combobox
                  placeholder="Busca o selecciona una universidad"
                  value={form.university}
                  options={universityOptions}
                  onChange={(value) =>
                    setForm({
                      ...form,
                      university: value,
                      academic_unit: 0,
                      career: 0,
                      study_plan: 0,
                      study_area: 0,
                    })
                  }
                />
              </div>
              <div>
                <Label htmlFor="subject-unit">Unidad académica</Label>
                <Combobox
                  placeholder={
                    form.university
                      ? "Busca o selecciona una unidad académica"
                      : "Primero elige la universidad"
                  }
                  value={form.academic_unit}
                  options={academicUnitOptions}
                  onChange={(value) =>
                    setForm({
                      ...form,
                      academic_unit: value,
                      career: 0,
                      study_plan: 0,
                      study_area: 0,
                    })
                  }
                />
              </div>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="subject-career">Carrera</Label>
                <Combobox
                  placeholder={
                    form.academic_unit
                      ? "Busca o selecciona una carrera"
                      : "Primero elige la unidad académica"
                  }
                  value={form.career}
                  options={careerOptions}
                  onChange={(value) =>
                    setForm({
                      ...form,
                      career: value,
                      study_plan: 0,
                      study_area: 0,
                    })
                  }
                />
              </div>
              <div>
                <Label htmlFor="subject-plan">Plan de estudios</Label>
                <Combobox
                  placeholder={
                    form.career
                      ? "Busca o selecciona un plan de estudios"
                      : "Primero elige la carrera"
                  }
                  value={form.study_plan}
                  options={planOptions}
                  onChange={(value) =>
                    setForm({
                      ...form,
                      study_plan: value,
                      study_area: 0,
                    })
                  }
                />
              </div>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="subject-area">Área</Label>
                <Combobox
                  placeholder={
                    form.study_plan
                      ? "Busca o selecciona un área"
                      : "Primero elige el plan de estudios"
                  }
                  value={form.study_area}
                  options={areaOptions}
                  onChange={(value) => setForm({ ...form, study_area: value })}
                />
              </div>
              <div>
                <Label htmlFor="subject-code">Código de la materia</Label>
                <Input
                  id="subject-code"
                  placeholder="Ej. MAT-101"
                  value={form.code}
                  onChange={(e) => setForm({ ...form, code: e.target.value })}
                />
              </div>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="sm:col-span-1">
                <Label htmlFor="subject-name">Nombre de la materia</Label>
                <Input
                  id="subject-name"
                  placeholder="Ej. Álgebra Lineal"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="subject-year">Año de dictado</Label>
                <Input
                  id="subject-year"
                  type="number"
                  min="1"
                  max={planDuration ? String(planDuration) : undefined}
                  placeholder={planDuration ? `1 a ${planDuration}` : "Año"}
                  value={String(form.year)}
                  onChange={(e) =>
                    setForm({ ...form, year: Number(e.target.value) || 0 })
                  }
                />
                {planDuration > 0 && (
                  <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
                    El plan dura {planDuration}{" "}
                    {planDuration === 1 ? "año" : "años"}.
                  </p>
                )}
              </div>
              <div>
                <Label htmlFor="subject-period">Período</Label>
                <select
                  id="subject-period"
                  value={form.period}
                  onChange={(e) => setForm({ ...form, period: e.target.value })}
                  className="h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800"
                >
                  {PERIOD_OPTIONS.map((p) => (
                    <option
                      key={p.value}
                      value={p.value}
                      className="bg-white text-gray-800 dark:bg-gray-900 dark:text-white/90"
                    >
                      {p.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="mt-5">
            <Switch
              label="Activa"
              defaultChecked={form.is_active}
              onChange={(checked) => setForm({ ...form, is_active: checked })}
            />
          </div>

          <div className="mt-6 flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={() => setModalOpen(false)}
              disabled={saving}
            >
              Cancelar
            </Button>
            <Button onClick={handleSubmit} disabled={saving}>
              {saving
                ? "Guardando…"
                : editing
                  ? "Guardar cambios"
                  : "Crear materia"}
            </Button>
          </div>
        </div>
      </Modal>

      <Modal
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        centered
        className="w-[40vw] max-w-[40vw]"
      >
        <div className="p-6 sm:p-8">
          <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-full bg-error-50 text-error-500 dark:bg-error-500/10">
            <TrashBinIcon className="size-5" />
          </div>
          <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
            Eliminar materia
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            ¿Estás seguro de eliminar la materia{" "}
            <span className="font-medium text-gray-700 dark:text-gray-300">
              {deleteTarget?.name}
            </span>
            ? Esta acción no se puede deshacer.
          </p>
          <div className="mt-6 flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={() => setDeleteTarget(null)}
              disabled={deleting}
            >
              Cancelar
            </Button>
            <Button
              variant="outline"
              onClick={confirmDelete}
              disabled={deleting}
              className="!border-error-500 !bg-error-500 !text-white hover:!bg-error-600"
            >
              {deleting ? "Eliminando…" : "Eliminar"}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
