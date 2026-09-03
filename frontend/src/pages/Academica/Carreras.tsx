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
import { Career, CareerPayload, careerApi } from "../../api/careers";
import { AcademicUnit, academicUnitApi } from "../../api/academicUnits";
import { Campus, campusApi } from "../../api/campuses";
import { University, universityApi } from "../../api/universities";

type CareerForm = CareerPayload & { university: number };

const EMPTY_FORM: CareerForm = {
  code: "",
  short_name: "",
  name: "",
  academic_unit: 0,
  campuses: [],
  is_active: true,
  university: 0,
};

export default function Carreras() {
  const [careers, setCareers] = useState<Career[]>([]);
  const [academicUnits, setAcademicUnits] = useState<AcademicUnit[]>([]);
  const [campuses, setCampuses] = useState<Campus[]>([]);
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Career | null>(null);
  const [form, setForm] = useState<CareerForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleteTarget, setDeleteTarget] = useState<Career | null>(null);
  const [deleting, setDeleting] = useState(false);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "inactive">("all");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [careersData, unitsData, campusesData, universitiesData] = await Promise.all([
        careerApi.list(),
        academicUnitApi.list(),
        campusApi.list(),
        universityApi.list(),
      ]);
      setCareers(careersData);
      setAcademicUnits(unitsData);
      setCampuses(campusesData);
      setUniversities(universitiesData);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "No se pudieron cargar las carreras.",
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
    label: u.short_name
      ? `${u.name} (${u.short_name})`
      : u.name,
  }));

  const unitCampuses = campuses.filter(
    (c) => c.academic_unit === form.academic_unit,
  );

  const filteredCareers = careers.filter((career) => {
    const term = search.trim().toLowerCase();
    const matchesSearch =
      !term ||
      career.name.toLowerCase().includes(term) ||
      career.code.toLowerCase().includes(term) ||
      career.short_name.toLowerCase().includes(term) ||
      career.academic_unit_name.toLowerCase().includes(term);
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "active" && career.is_active) ||
      (statusFilter === "inactive" && !career.is_active);
    return matchesSearch && matchesStatus;
  });

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  };

  const openEdit = (career: Career) => {
    const unit = academicUnits.find((u) => u.id === career.academic_unit);
    setEditing(career);
    setForm({
      code: career.code,
      short_name: career.short_name,
      name: career.name,
      academic_unit: career.academic_unit,
      campuses: [...career.campuses],
      is_active: career.is_active,
      university: unit ? unit.university : 0,
    });
    setFormError(null);
    setModalOpen(true);
  };

  const toggleCampus = (campusId: number) => {
    setForm((prev) => {
      const has = prev.campuses.includes(campusId);
      return {
        ...prev,
        campuses: has
          ? prev.campuses.filter((id) => id !== campusId)
          : [...prev.campuses, campusId],
      };
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
    if (!form.code.trim() || !form.name.trim() || !form.short_name.trim()) {
      setFormError("El código, el nombre corto y el nombre son obligatorios.");
      return;
    }
    setSaving(true);
    try {
      if (editing) {
        await careerApi.update(editing.id, form);
      } else {
        await careerApi.create(form);
      }
      setModalOpen(false);
      fetchData();
    } catch (e) {
      setFormError(
        e instanceof Error ? e.message : "No se pudo guardar la carrera.",
      );
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await careerApi.remove(deleteTarget.id);
      setDeleteTarget(null);
      fetchData();
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "No se pudo eliminar la carrera.",
      );
      setDeleteTarget(null);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div>
      <PageMeta title="Academix" description="Gestión de carreras" />
      <PageBreadcrumb pageTitle="Carreras" />

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
            Nueva carrera
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
              Listado de carreras
            </h2>
          </div>

          <div className="flex flex-col gap-3 border-b border-gray-200 px-5 py-4 dark:border-gray-800 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar por nombre, código, nombre corto o unidad académica…"
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
                Cargando carreras…
              </div>
            ) : filteredCareers.length === 0 ? (
              <div className="px-5 py-10 text-center text-sm text-gray-500 dark:text-gray-400">
                No se encontraron carreras con los criterios de búsqueda.
              </div>
            ) : (
              <table className="w-full min-w-[720px] text-left text-sm">
                <thead className="bg-gray-50 text-xs uppercase text-gray-500 dark:bg-white/[0.02] dark:text-gray-400">
                  <tr>
                    <th className="px-5 py-3">Código</th>
                    <th className="px-5 py-3">Nombre</th>
                    <th className="px-5 py-3">Unidad académica</th>
                    <th className="px-5 py-3">Sedes</th>
                    <th className="px-5 py-3">Estado</th>
                    <th className="px-5 py-3 text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {filteredCareers.map((career) => (
                    <tr
                      key={career.id}
                      className="hover:bg-gray-50 dark:hover:bg-white/[0.02]"
                    >
                      <td className="px-5 py-4 font-medium text-gray-900 dark:text-white">
                        {career.code}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        <div className="font-medium text-gray-800 dark:text-white">
                          {career.name}
                        </div>
                        <div className="text-xs text-gray-400 dark:text-gray-500">
                          {career.short_name}
                        </div>
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        {career.academic_unit_name}
                      </td>
                      <td className="px-5 py-4">
                        {career.campus_details.length === 0 ? (
                          <span className="text-gray-400">—</span>
                        ) : (
                          <div className="flex flex-wrap gap-1.5">
                            {career.campus_details.map((c) => (
                              <span
                                key={c.id}
                                title={c.name}
                                className="inline-flex items-center rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700 dark:bg-white/5 dark:text-gray-300"
                              >
                                {c.code}
                              </span>
                            ))}
                          </div>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        {career.is_active ? (
                          <Badge color="success">Activa</Badge>
                        ) : (
                          <Badge color="warning">Inactiva</Badge>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => openEdit(career)}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-gray-100 hover:text-brand-500 dark:text-gray-400 dark:hover:bg-white/5"
                            aria-label={`Editar ${career.name}`}
                            title="Editar"
                          >
                            <PencilIcon className="size-4" />
                          </button>
                          <button
                            onClick={() => setDeleteTarget(career)}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-error-50 hover:text-error-500 dark:text-gray-400 dark:hover:bg-error-500/10"
                            aria-label={`Eliminar ${career.name}`}
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
            {editing ? "Editar carrera" : "Nueva carrera"}
          </h3>

          {formError && (
            <div className="mb-4 rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
              {formError}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <Label htmlFor="career-university">Universidad</Label>
              <Combobox
                placeholder="Busca o selecciona una universidad"
                value={form.university}
                options={universityOptions}
                onChange={(value) =>
                  setForm({
                    ...form,
                    university: value,
                    academic_unit: 0,
                    campuses: [],
                  })
                }
              />
            </div>
            <div>
              <Label htmlFor="career-unit">Unidad académica</Label>
              <Combobox
                placeholder={
                  form.university
                    ? "Busca o selecciona una unidad académica"
                    : "Primero elige la universidad"
                }
                value={form.academic_unit}
                options={academicUnitOptions}
                onChange={(value) =>
                  setForm({ ...form, academic_unit: value, campuses: [] })
                }
              />
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div>
                <Label htmlFor="career-code">Código</Label>
                <Input
                  id="career-code"
                  placeholder="Ej. ING-01"
                  value={form.code}
                  onChange={(e) => setForm({ ...form, code: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="career-short">Nombre corto</Label>
                <Input
                  id="career-short"
                  placeholder="Ej. Ing. Informática"
                  value={form.short_name}
                  onChange={(e) =>
                    setForm({ ...form, short_name: e.target.value })
                  }
                />
              </div>
              <div>
                <Label htmlFor="career-name">Nombre</Label>
                <Input
                  id="career-name"
                  placeholder="Ej. Ingeniería en Informática"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>
            </div>
            <div>
              <Label>Sedes donde se dicta</Label>
              <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-800">
                {unitCampuses.length === 0 ? (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    No hay sedes para la unidad académica seleccionada.
                  </p>
                ) : (
                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                    {unitCampuses.map((campus) => {
                      const checked = form.campuses.includes(campus.id);
                      return (
                        <label
                          key={campus.id}
                          className="flex cursor-pointer items-center gap-3 rounded-lg px-2 py-2 transition-colors hover:bg-gray-50 dark:hover:bg-white/[0.03]"
                        >
                          <input
                            type="checkbox"
                            checked={checked}
                            onChange={() => toggleCampus(campus.id)}
                            className="size-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500 dark:border-gray-700 dark:bg-gray-900"
                          />
                          <span className="text-sm text-gray-700 dark:text-gray-300">
                            {campus.name}
                            <span className="ml-1 text-xs text-gray-400">
                              {campus.code}
                            </span>
                          </span>
                        </label>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="mt-5">
            <Switch
              label="Carrera activa"
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
                  : "Crear carrera"}
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
            Eliminar carrera
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            ¿Estás seguro de eliminar{" "}
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
