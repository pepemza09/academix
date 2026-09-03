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
import { StudyPlan, StudyPlanPayload, studyPlanApi } from "../../api/studyPlans";
import { Career, careerApi } from "../../api/careers";
import { AcademicUnit, academicUnitApi } from "../../api/academicUnits";
import { University, universityApi } from "../../api/universities";

type PlanForm = StudyPlanPayload & { university: number; academic_unit: number };

const EMPTY_FORM: PlanForm = {
  code: "",
  title: "",
  intermediate_title: "",
  career: 0,
  is_active: true,
  is_current: false,
  university: 0,
  academic_unit: 0,
};

export default function Planes() {
  const [plans, setPlans] = useState<StudyPlan[]>([]);
  const [careers, setCareers] = useState<Career[]>([]);
  const [academicUnits, setAcademicUnits] = useState<AcademicUnit[]>([]);
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<StudyPlan | null>(null);
  const [form, setForm] = useState<PlanForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleteTarget, setDeleteTarget] = useState<StudyPlan | null>(null);
  const [deleting, setDeleting] = useState(false);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "inactive">("all");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [plansData, careersData, unitsData, universitiesData] =
        await Promise.all([
          studyPlanApi.list(),
          careerApi.list(),
          academicUnitApi.list(),
          universityApi.list(),
        ]);
      setPlans(plansData);
      setCareers(careersData);
      setAcademicUnits(unitsData);
      setUniversities(universitiesData);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "No se pudieron cargar los planes de estudio.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

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

  const filteredPlans = plans.filter((plan) => {
    const term = search.trim().toLowerCase();
    const matchesSearch =
      !term ||
      plan.code.toLowerCase().includes(term) ||
      plan.title.toLowerCase().includes(term) ||
      plan.intermediate_title.toLowerCase().includes(term) ||
      plan.career_name.toLowerCase().includes(term) ||
      plan.career_code.toLowerCase().includes(term);
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "active" && plan.is_active) ||
      (statusFilter === "inactive" && !plan.is_active);
    return matchesSearch && matchesStatus;
  });

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  };

  const openEdit = (plan: StudyPlan) => {
    const career = careers.find((c) => c.id === plan.career);
    const unit = career
      ? academicUnits.find((u) => u.id === career.academic_unit)
      : undefined;
    setEditing(plan);
    setForm({
      code: plan.code,
      title: plan.title,
      intermediate_title: plan.intermediate_title,
      career: plan.career,
      is_active: plan.is_active,
      is_current: plan.is_current,
      university: unit ? unit.university : 0,
      academic_unit: career ? career.academic_unit : 0,
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
    if (!form.code.trim() || !form.title.trim()) {
      setFormError("El código del plan y el título que otorga son obligatorios.");
      return;
    }
    setSaving(true);
    try {
      if (editing) {
        const updated = await studyPlanApi.update(editing.id, form);
        setPlans((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
      } else {
        const created = await studyPlanApi.create(form);
        setPlans((prev) => [...prev, created]);
      }
      setModalOpen(false);
    } catch (e) {
      setFormError(
        e instanceof Error ? e.message : "No se pudo guardar el plan.",
      );
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await studyPlanApi.remove(deleteTarget.id);
      setPlans((prev) => prev.filter((p) => p.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "No se pudo eliminar el plan.",
      );
      setDeleteTarget(null);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div>
      <PageMeta title="Academix" description="Gestión de planes de estudio" />
      <PageBreadcrumb pageTitle="Planes" />

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
            Nuevo plan
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
              Listado de planes de estudio
            </h2>
          </div>

          <div className="flex flex-col gap-3 border-b border-gray-200 px-5 py-4 dark:border-gray-800 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar por código, título o carrera…"
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
                  Todos
                </option>
                <option value="active" className="bg-white text-gray-800 dark:bg-gray-900 dark:text-white/90">
                  Solo activos
                </option>
                <option value="inactive" className="bg-white text-gray-800 dark:bg-gray-900 dark:text-white/90">
                  Solo inactivos
                </option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            {loading ? (
              <div className="px-5 py-10 text-center text-sm text-gray-500 dark:text-gray-400">
                Cargando planes…
              </div>
            ) : filteredPlans.length === 0 ? (
              <div className="px-5 py-10 text-center text-sm text-gray-500 dark:text-gray-400">
                No se encontraron planes con los criterios de búsqueda.
              </div>
            ) : (
              <table className="w-full min-w-[860px] text-left text-sm">
                <thead className="bg-gray-50 text-xs uppercase text-gray-500 dark:bg-white/[0.02] dark:text-gray-400">
                  <tr>
                    <th className="px-5 py-3">Código</th>
                    <th className="px-5 py-3">Título que otorga</th>
                    <th className="px-5 py-3">Título intermedio</th>
                    <th className="px-5 py-3">Carrera</th>
                    <th className="px-5 py-3">Activo</th>
                    <th className="px-5 py-3">Vigente</th>
                    <th className="px-5 py-3 text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {filteredPlans.map((plan) => (
                    <tr
                      key={plan.id}
                      className="hover:bg-gray-50 dark:hover:bg-white/[0.02]"
                    >
                      <td className="px-5 py-4 font-medium text-gray-900 dark:text-white">
                        {plan.code}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        {plan.title}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        {plan.intermediate_title || (
                          <span className="text-gray-400 dark:text-gray-500">—</span>
                        )}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        <div className="font-medium text-gray-800 dark:text-white">
                          {plan.career_name}
                        </div>
                        <div className="text-xs text-gray-400 dark:text-gray-500">
                          {plan.career_code}
                        </div>
                      </td>
                      <td className="px-5 py-4">
                        {plan.is_active ? (
                          <Badge color="success">Activo</Badge>
                        ) : (
                          <Badge color="warning">Inactivo</Badge>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        {plan.is_current ? (
                          <Badge color="success">Vigente</Badge>
                        ) : (
                          <Badge color="light">No vigente</Badge>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => openEdit(plan)}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-gray-100 hover:text-brand-500 dark:text-gray-400 dark:hover:bg-white/5"
                            aria-label={`Editar ${plan.code}`}
                            title="Editar"
                          >
                            <PencilIcon className="size-4" />
                          </button>
                          <button
                            onClick={() => setDeleteTarget(plan)}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-error-50 hover:text-error-500 dark:text-gray-400 dark:hover:bg-error-500/10"
                            aria-label={`Eliminar ${plan.code}`}
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
            {editing ? "Editar plan" : "Nuevo plan de estudio"}
          </h3>

          {formError && (
            <div className="mb-4 rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
              {formError}
            </div>
          )}

          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div>
                <Label htmlFor="plan-university">Universidad</Label>
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
                    })
                  }
                />
              </div>
              <div>
                <Label htmlFor="plan-unit">Unidad académica</Label>
                <Combobox
                  placeholder={
                    form.university
                      ? "Busca o selecciona una unidad académica"
                      : "Primero elige la universidad"
                  }
                  value={form.academic_unit}
                  options={academicUnitOptions}
                  onChange={(value) =>
                    setForm({ ...form, academic_unit: value, career: 0 })
                  }
                />
              </div>
              <div>
                <Label htmlFor="plan-career">Carrera</Label>
                <Combobox
                  placeholder={
                    form.academic_unit
                      ? "Busca o selecciona una carrera"
                      : "Primero elige la unidad académica"
                  }
                  value={form.career}
                  options={careerOptions}
                  onChange={(value) =>
                    setForm({ ...form, career: value })
                  }
                />
              </div>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="plan-code">Código del plan</Label>
                <Input
                  id="plan-code"
                  placeholder="Ej. PLAN-2010"
                  value={form.code}
                  onChange={(e) => setForm({ ...form, code: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="plan-title">Título que otorga</Label>
                <Input
                  id="plan-title"
                  placeholder="Ej. Ingeniero en Informática"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="plan-intermediate-title">
                  Título intermedio
                </Label>
                <Input
                  id="plan-intermediate-title"
                  placeholder="Ej. Técnico Universitario en Informática (opcional)"
                  value={form.intermediate_title}
                  onChange={(e) =>
                    setForm({ ...form, intermediate_title: e.target.value })
                  }
                />
              </div>
            </div>
          </div>

          <div className="mt-5 flex flex-col gap-4 sm:flex-row sm:gap-10">
            <Switch
              label="Activo"
              defaultChecked={form.is_active}
              onChange={(checked) => setForm({ ...form, is_active: checked })}
            />
            <Switch
              label="Vigente"
              defaultChecked={form.is_current}
              onChange={(checked) => setForm({ ...form, is_current: checked })}
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
                  : "Crear plan"}
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
            Eliminar plan de estudio
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            ¿Estás seguro de eliminar el plan{" "}
            <span className="font-medium text-gray-700 dark:text-gray-300">
              {deleteTarget?.code}
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
