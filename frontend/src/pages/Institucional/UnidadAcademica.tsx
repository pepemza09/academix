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
  AcademicUnit,
  academicUnitApi,
  AcademicUnitPayload,
} from "../../api/academicUnits";
import {
  University,
  universityApi,
} from "../../api/universities";

const EMPTY_FORM: AcademicUnitPayload = {
  code: "",
  short_name: "",
  name: "",
  university: 0,
  is_active: true,
};

export default function UnidadAcademica() {
  const [units, setUnits] = useState<AcademicUnit[]>([]);
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<AcademicUnit | null>(null);
  const [form, setForm] = useState<AcademicUnitPayload>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleteTarget, setDeleteTarget] = useState<AcademicUnit | null>(null);
  const [deleting, setDeleting] = useState(false);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "inactive">("all");

  const filteredUnits = units.filter((unit) => {
    const term = search.trim().toLowerCase();
    const matchesSearch =
      !term ||
      unit.name.toLowerCase().includes(term) ||
      unit.code.toLowerCase().includes(term) ||
      unit.university_name.toLowerCase().includes(term);
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "active" && unit.is_active) ||
      (statusFilter === "inactive" && !unit.is_active);
    return matchesSearch && matchesStatus;
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [unitsData, universitiesData] = await Promise.all([
        academicUnitApi.list(),
        universityApi.list(),
      ]);
      setUnits(unitsData);
      setUniversities(universitiesData);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "No se pudieron cargar las unidades académicas.",
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
    label: u.short_name
      ? `${u.name} (${u.short_name})`
      : u.name,
  }));

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  };

  const openEdit = (unit: AcademicUnit) => {
    setEditing(unit);
    setForm({
      code: unit.code,
      short_name: unit.short_name,
      name: unit.name,
      university: unit.university,
      is_active: unit.is_active,
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
    if (!form.code.trim() || !form.name.trim()) {
      setFormError("El código y el nombre son obligatorios.");
      return;
    }
    setSaving(true);
    try {
      if (editing) {
        await academicUnitApi.update(editing.id, form);
      } else {
        await academicUnitApi.create(form);
      }
      setModalOpen(false);
      fetchData();
    } catch (e) {
      setFormError(
        e instanceof Error ? e.message : "No se pudo guardar la unidad.",
      );
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await academicUnitApi.remove(deleteTarget.id);
      setDeleteTarget(null);
      fetchData();
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "No se pudo eliminar la unidad.",
      );
      setDeleteTarget(null);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div>
      <PageMeta
        title="Academix | Unidad Académica"
        description="Gestión de unidades académicas"
      />
      <PageBreadcrumb pageTitle="Unidades Académicas" />

      <div className="space-y-6">
        <div className="flex justify-end">
          <Button onClick={openCreate} size="sm" className="font-bold">
            Nueva unidad académica
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
              Listado de unidades académicas
            </h2>
          </div>

          <div className="flex flex-col gap-3 border-b border-gray-200 px-5 py-4 dark:border-gray-800 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar por nombre, código o universidad…"
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
                Cargando unidades académicas…
              </div>
            ) : filteredUnits.length === 0 ? (
              <div className="px-5 py-10 text-center text-sm text-gray-500 dark:text-gray-400">
                No se encontraron unidades con los criterios de búsqueda.
              </div>
            ) : (
              <table className="w-full min-w-[900px] text-left text-sm">
                <thead className="bg-gray-50 text-xs uppercase text-gray-500 dark:bg-white/[0.02] dark:text-gray-400">
                  <tr>
                    <th className="px-5 py-3">Universidad</th>
                    <th className="px-5 py-3">Código</th>
                    <th className="px-5 py-3">Nombre corto</th>
                    <th className="px-5 py-3">Nombre</th>
                    <th className="px-5 py-3">Estado</th>
                    <th className="px-5 py-3 text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {filteredUnits.map((unit) => (
                    <tr
                      key={unit.id}
                      className="hover:bg-gray-50 dark:hover:bg-white/[0.02]"
                    >
                      <td className="px-5 py-4 font-medium text-gray-900 dark:text-white">
                        {unit.university_name}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        {unit.code}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        {unit.short_name || (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        {unit.name}
                      </td>
                      <td className="px-5 py-4">
                        {unit.is_active ? (
                          <Badge color="success">Activa</Badge>
                        ) : (
                          <Badge color="warning">Inactiva</Badge>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => openEdit(unit)}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-gray-100 hover:text-brand-500 dark:text-gray-400 dark:hover:bg-white/5"
                            aria-label={`Editar ${unit.name}`}
                            title="Editar"
                          >
                            <PencilIcon className="size-4" />
                          </button>
                          <button
                            onClick={() => setDeleteTarget(unit)}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-error-50 hover:text-error-500 dark:text-gray-400 dark:hover:bg-error-500/10"
                            aria-label={`Eliminar ${unit.name}`}
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
            {editing ? "Editar unidad académica" : "Nueva unidad académica"}
          </h3>

          {formError && (
            <div className="mb-4 rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
              {formError}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <Label htmlFor="unit-university">Universidad</Label>
              <Combobox
                placeholder="Busca o selecciona una universidad"
                value={form.university}
                options={universityOptions}
                onChange={(value) =>
                  setForm({ ...form, university: value })
                }
              />
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="unit-code">Código</Label>
                <Input
                  id="unit-code"
                  placeholder="Ej. FAC-01"
                  value={form.code}
                  onChange={(e) => setForm({ ...form, code: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="unit-short-name">Nombre corto</Label>
                <Input
                  id="unit-short-name"
                  placeholder="Ej. Ingeniería"
                  value={form.short_name}
                  onChange={(e) =>
                    setForm({ ...form, short_name: e.target.value })
                  }
                />
              </div>
            </div>
            <div>
              <Label htmlFor="unit-name">Nombre completo</Label>
              <Input
                id="unit-name"
                placeholder="Ej. Facultad de Ingeniería"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>
          </div>

          <div className="mt-5">
            <Switch
              label="Unidad activa"
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
                  : "Crear unidad"}
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
            Eliminar unidad académica
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
