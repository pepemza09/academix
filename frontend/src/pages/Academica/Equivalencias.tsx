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
  Equivalence,
  EquivalencePayload,
  EquivalenceSubjectRef,
  equivalenceApi,
} from "../../api/equivalences";
import { Subject } from "../../api/subjects";
import { StudyArea } from "../../api/studyAreas";
import { StudyPlan } from "../../api/studyPlans";
import { Career } from "../../api/careers";
import { AcademicUnit } from "../../api/academicUnits";
import { University } from "../../api/universities";
import { formOptionsApi } from "../../api/formOptions";

interface EquivalenceForm extends EquivalencePayload {
  university: number;
  academic_unit: number;
  career: number;
  new_plan: number;
  old_plan: number;
}

const EMPTY_FORM: EquivalenceForm = {
  new_subjects: [],
  old_subjects: [],
  rule_text: "",
  is_active: true,
  university: 0,
  academic_unit: 0,
  career: 0,
  new_plan: 0,
  old_plan: 0,
};

function groupByPlan(details: EquivalenceSubjectRef[]) {
  const groups = new Map<string, EquivalenceSubjectRef[]>();
  for (const s of details) {
    const key = `${s.study_plan_code} - ${s.study_plan_title}`;
    const list = groups.get(key);
    if (list) list.push(s);
    else groups.set(key, [s]);
  }
  return [...groups.entries()];
}

export default function Equivalencias() {
  const [equivalences, setEquivalences] = useState<Equivalence[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [areas, setAreas] = useState<StudyArea[]>([]);
  const [plans, setPlans] = useState<StudyPlan[]>([]);
  const [careers, setCareers] = useState<Career[]>([]);
  const [academicUnits, setAcademicUnits] = useState<AcademicUnit[]>([]);
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Equivalence | null>(null);
  const [form, setForm] = useState<EquivalenceForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleteTarget, setDeleteTarget] = useState<Equivalence | null>(null);
  const [deleting, setDeleting] = useState(false);

  const [search, setSearch] = useState("");
  const [planFilter, setPlanFilter] = useState(0);
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "inactive">("all");
  const [newSearch, setNewSearch] = useState("");
  const [oldSearch, setOldSearch] = useState("");

  const fetchData = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const [options, items] = await Promise.all([
        formOptionsApi.list(signal),
        equivalenceApi.list(signal),
      ]);
      setSubjects(options.subjects);
      setAreas(options.study_areas);
      setPlans(options.study_plans);
      setCareers(options.careers);
      setAcademicUnits(options.academic_units);
      setUniversities(options.universities);
      setEquivalences(items);
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") return;
      setError(
        e instanceof Error
          ? e.message
          : "No se pudieron cargar las equivalencias.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetchData(controller.signal);
    return () => controller.abort();
  }, [fetchData]);

  const areaById = new Map(areas.map((a) => [a.id, a]));

  const subjectsOfPlan = (planId: number) =>
    subjects
      .filter((s) => areaById.get(s.study_area)?.study_plan === planId)
      .sort((a, b) => a.code.localeCompare(b.code, "es"));

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

  const filteredEquivalences = equivalences.filter((eq) => {
    const term = search.trim().toLowerCase();
    const haystack = [
      eq.rule_text,
      ...eq.new_details.flatMap((s) => [s.code, s.name]),
      ...eq.old_details.flatMap((s) => [s.code, s.name]),
    ]
      .join(" ")
      .toLowerCase();
    const matchesSearch = !term || haystack.includes(term);
    const matchesPlan =
      !planFilter ||
      eq.new_details.some((s) => s.study_plan === planFilter) ||
      eq.old_details.some((s) => s.study_plan === planFilter);
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "active" && eq.is_active) ||
      (statusFilter === "inactive" && !eq.is_active);
    return matchesSearch && matchesPlan && matchesStatus;
  });

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setNewSearch("");
    setOldSearch("");
    setModalOpen(true);
  };

  const openEdit = (eq: Equivalence) => {
    const firstNew = eq.new_details[0];
    const firstOld = eq.old_details[0];
    const plan = firstNew
      ? plans.find((p) => p.id === firstNew.study_plan)
      : firstOld
        ? plans.find((p) => p.id === firstOld.study_plan)
        : undefined;
    const career = plan
      ? careers.find((c) => c.id === plan.career)
      : undefined;
    const unit = career
      ? academicUnits.find((u) => u.id === career.academic_unit)
      : undefined;
    setEditing(eq);
    setNewSearch("");
    setOldSearch("");
    setForm({
      new_subjects: [...eq.new_subjects],
      old_subjects: [...eq.old_subjects],
      rule_text: eq.rule_text || "",
      is_active: eq.is_active,
      career: career ? career.id : 0,
      new_plan: firstNew ? firstNew.study_plan : 0,
      old_plan: firstOld ? firstOld.study_plan : 0,
      university: unit ? unit.university : 0,
      academic_unit: career ? career.academic_unit : 0,
    });
    setFormError(null);
    setModalOpen(true);
  };

  const toggleSubject = (side: "new" | "old", id: number) => {
    setForm((prev) => {
      const key = side === "new" ? "new_subjects" : "old_subjects";
      const current = new Set(prev[key]);
      if (current.has(id)) current.delete(id);
      else current.add(id);
      return { ...prev, [key]: [...current] };
    });
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
    if (
      form.new_subjects.length === 0 &&
      form.old_subjects.length === 0 &&
      !form.rule_text.trim()
    ) {
      setFormError(
        "Debe indicar materias de al menos un lado o una regla de certificación.",
      );
      return;
    }
    if (form.new_plan && form.new_plan === form.old_plan) {
      setFormError(
        "Los dos lados de la equivalencia deben pertenecer a planes de estudio distintos.",
      );
      return;
    }
    const overlap = form.new_subjects.filter((id) =>
      form.old_subjects.includes(id),
    );
    if (overlap.length > 0) {
      setFormError(
        "Una materia no puede estar en ambos lados de la equivalencia.",
      );
      return;
    }
    const payload: EquivalencePayload = {
      new_subjects: form.new_subjects,
      old_subjects: form.old_subjects,
      rule_text: form.rule_text.trim(),
      is_active: form.is_active,
    };
    setSaving(true);
    try {
      if (editing) {
        const updated = await equivalenceApi.update(editing.id, payload);
        setEquivalences((prev) =>
          prev.map((e) => (e.id === updated.id ? updated : e)),
        );
      } else {
        const created = await equivalenceApi.create(payload);
        setEquivalences((prev) => [...prev, created]);
      }
      setModalOpen(false);
    } catch (e) {
      setFormError(
        e instanceof Error ? e.message : "No se pudo guardar la equivalencia.",
      );
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await equivalenceApi.remove(deleteTarget.id);
      setEquivalences((prev) => prev.filter((e) => e.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "No se pudo eliminar la equivalencia.",
      );
      setDeleteTarget(null);
    } finally {
      setDeleting(false);
    }
  };

  const careerOptions = (
    form.academic_unit
      ? careers.filter((c) => c.academic_unit === form.academic_unit)
      : []
  ).map((c) => ({
    value: c.id,
    label: c.short_name ? `${c.name} (${c.short_name})` : c.name,
  }));

  const planOptions = (
    form.career ? plans.filter((p) => p.career === form.career) : []
  ).map((p) => ({
    value: p.id,
    label: `${p.code} - ${p.title}${p.is_current ? " (vigente)" : ""}`,
  }));

  const planFilterOptions = plans.map((p) => ({
    value: String(p.id),
    label: `${p.code} - ${p.title}`,
  }));

  const renderSide = (details: EquivalenceSubjectRef[]) => {
    if (details.length === 0)
      return (
        <span className="text-gray-400 dark:text-gray-500">—</span>
      );
    return (
      <div className="space-y-2">
        {groupByPlan(details).map(([plan, list]) => (
          <div key={plan}>
            <div className="text-xs font-medium text-gray-400 dark:text-gray-500">
              {plan}
            </div>
            <div className="mt-1 flex flex-wrap gap-1">
              {list.map((s) => (
                <span
                  key={s.id}
                  title={`${s.code} - ${s.name}`}
                  className="inline-block max-w-[260px] truncate rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-700 dark:bg-white/5 dark:text-gray-300"
                >
                  {s.code} — {s.name}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderCheckboxes = (
    planId: number,
    selected: number[],
    side: "new" | "old",
  ) => {
    if (!planId)
      return (
        <p className="text-xs text-gray-400 dark:text-gray-500">
          Primero elige el plan de estudios.
        </p>
      );
    const all = subjectsOfPlan(planId);
    if (all.length === 0)
      return (
        <p className="text-xs text-gray-400 dark:text-gray-500">
          El plan no tiene materias.
        </p>
      );
    const query = side === "new" ? newSearch : oldSearch;
    const setQuery = side === "new" ? setNewSearch : setOldSearch;
    const term = query.trim().toLowerCase();
    const list = term
      ? all.filter((s) =>
          `${s.code} ${s.name}`.toLowerCase().includes(term),
        )
      : all;
    return (
      <div className="space-y-2">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar por código o nombre…"
            className="h-10 w-full rounded-lg border border-gray-300 bg-transparent px-3 pr-9 text-sm shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
          />
          <svg
            className="absolute right-3 top-1/2 size-4 -translate-y-1/2 text-gray-400"
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
        {list.length === 0 ? (
          <p className="rounded-lg border border-gray-200 px-3 py-4 text-center text-xs text-gray-400 dark:border-gray-800 dark:text-gray-500">
            Sin resultados para “{query.trim()}”.
          </p>
        ) : (
          <div className="max-h-56 space-y-1 overflow-y-auto rounded-lg border border-gray-200 p-3 dark:border-gray-800">
            {list.map((s) => (
              <label
                key={s.id}
                className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-white/5"
              >
                <input
                  type="checkbox"
                  checked={selected.includes(s.id)}
                  onChange={() => toggleSubject(side, s.id)}
                  className="h-4 w-4 accent-brand-500"
                />
                <span className="font-medium">{s.code}</span>
                <span className="truncate">{s.name}</span>
              </label>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      <PageMeta title="Academix" description="Gestión de equivalencias" />
      <PageBreadcrumb pageTitle="Equivalencias" />

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
            Nueva equivalencia
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
              Listado de equivalencias
            </h2>
          </div>

          <div className="flex flex-col gap-3 border-b border-gray-200 px-5 py-4 dark:border-gray-800 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar por código, nombre o regla…"
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
            <div className="w-full sm:w-64">
              <select
                value={planFilter ? String(planFilter) : ""}
                onChange={(e) => setPlanFilter(Number(e.target.value) || 0)}
                className="h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800"
              >
                <option value="" className="bg-white text-gray-800 dark:bg-gray-900 dark:text-white/90">
                  Todos los planes
                </option>
                {planFilterOptions.map((o) => (
                  <option key={o.value} value={o.value} className="bg-white text-gray-800 dark:bg-gray-900 dark:text-white/90">
                    {o.label}
                  </option>
                ))}
              </select>
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
                Cargando equivalencias…
              </div>
            ) : filteredEquivalences.length === 0 ? (
              <div className="px-5 py-10 text-center text-sm text-gray-500 dark:text-gray-400">
                No se encontraron equivalencias con los criterios de búsqueda.
              </div>
            ) : (
              <table className="w-full min-w-[980px] text-left text-sm">
                <thead className="bg-gray-50 text-xs uppercase text-gray-500 dark:bg-white/[0.02] dark:text-gray-400">
                  <tr>
                    <th className="px-5 py-3">Plan reciente</th>
                    <th className="px-5 py-3">Planes anteriores</th>
                    <th className="px-5 py-3">Regla</th>
                    <th className="px-5 py-3">Activa</th>
                    <th className="px-5 py-3 text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {filteredEquivalences.map((eq) => (
                    <tr
                      key={eq.id}
                      className="hover:bg-gray-50 dark:hover:bg-white/[0.02]"
                    >
                      <td className="px-5 py-4">
                        {renderSide(eq.new_details)}
                      </td>
                      <td className="px-5 py-4">
                        {renderSide(eq.old_details)}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        {eq.rule_text || (
                          <span className="text-gray-400 dark:text-gray-500">
                            —
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        {eq.is_active ? (
                          <Badge color="success">Activa</Badge>
                        ) : (
                          <Badge color="warning">Inactiva</Badge>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => openEdit(eq)}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-gray-100 hover:text-brand-500 dark:text-gray-400 dark:hover:bg-white/5"
                            aria-label="Editar equivalencia"
                            title="Editar"
                          >
                            <PencilIcon className="size-4" />
                          </button>
                          <button
                            onClick={() => setDeleteTarget(eq)}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-error-50 hover:text-error-500 dark:text-gray-400 dark:hover:bg-error-500/10"
                            aria-label="Eliminar equivalencia"
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
            {editing ? "Editar equivalencia" : "Nueva equivalencia"}
          </h3>

          {formError && (
            <div className="mb-4 rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
              {formError}
            </div>
          )}

          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div>
                <Label>Universidad</Label>
                <Combobox
                  placeholder="Busca o selecciona una universidad"
                  value={form.university}
                  options={universityOptions}
                  onChange={(value) =>
                    setForm({
                      ...EMPTY_FORM,
                      university: value,
                    })
                  }
                />
              </div>
              <div>
                <Label>Unidad académica</Label>
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
                      ...EMPTY_FORM,
                      university: form.university,
                      academic_unit: value,
                    })
                  }
                />
              </div>
              <div>
                <Label>Carrera</Label>
                <Combobox
                  placeholder={
                    form.academic_unit
                      ? "Busca o selecciona una carrera"
                      : "Primero elige la unidad académica"
                  }
                  value={form.career}
                  options={careerOptions}
                  onChange={(value) => {
                    setNewSearch("");
                    setOldSearch("");
                    setForm((prev) => ({
                      ...prev,
                      career: value,
                      new_plan: 0,
                      old_plan: 0,
                      new_subjects: [],
                      old_subjects: [],
                    }));
                  }}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label>Plan reciente (se muestra primero)</Label>
                <Combobox
                  placeholder={
                    form.career
                      ? "Busca o selecciona el plan reciente"
                      : "Primero elige la carrera"
                  }
                  value={form.new_plan}
                  options={planOptions}
                  onChange={(value) => {
                    setNewSearch("");
                    setForm((prev) => ({
                      ...prev,
                      new_plan: value,
                      new_subjects: [],
                    }));
                  }}
                />
                <div className="mt-2">
                  {renderCheckboxes(
                    form.new_plan,
                    form.new_subjects,
                    "new",
                  )}
                </div>
              </div>
              <div>
                <Label>Planes anteriores</Label>
                <Combobox
                  placeholder={
                    form.career
                      ? "Busca o selecciona el plan anterior"
                      : "Primero elige la carrera"
                  }
                  value={form.old_plan}
                  options={planOptions}
                  onChange={(value) => {
                    setOldSearch("");
                    setForm((prev) => ({
                      ...prev,
                      old_plan: value,
                      old_subjects: [],
                    }));
                  }}
                />
                <div className="mt-2">
                  {renderCheckboxes(
                    form.old_plan,
                    form.old_subjects,
                    "old",
                  )}
                </div>
              </div>
            </div>

            <div>
              <Label htmlFor="equivalence-rule">
                Regla de certificación (opcional)
              </Label>
              <Input
                id="equivalence-rule"
                placeholder="Ej. Certifica Inglés"
                value={form.rule_text}
                onChange={(e) =>
                  setForm({ ...form, rule_text: e.target.value })
                }
              />
              <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
                Para casos que no son materia ↔ materia (inglés, actividad
                física, práctica socioeducativa).
              </p>
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
                  : "Crear equivalencia"}
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
            Eliminar equivalencia
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            ¿Estás seguro de eliminar esta equivalencia
            {deleteTarget?.rule_text
              ? ` (${deleteTarget.rule_text})`
              : ""}
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
