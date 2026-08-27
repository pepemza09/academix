import { useCallback, useEffect, useState } from "react";
import PageMeta from "../../components/common/PageMeta";
import Button from "../../components/ui/button/Button";
import { Modal } from "../../components/ui/modal";
import Input from "../../components/form/input/InputField";
import Label from "../../components/form/Label";
import Badge from "../../components/ui/badge/Badge";
import { PlusIcon, PencilIcon, TrashBinIcon } from "../../icons";
import {
  AcademicUnit,
  academicUnitApi,
  AcademicUnitPayload,
} from "../../api/academicUnits";

const EMPTY_FORM: AcademicUnitPayload = {
  code: "",
  short_name: "",
  name: "",
  is_active: true,
};

export default function AcademicsHome() {
  const [units, setUnits] = useState<AcademicUnit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<AcademicUnit | null>(null);
  const [form, setForm] = useState<AcademicUnitPayload>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleteTarget, setDeleteTarget] = useState<AcademicUnit | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchUnits = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await academicUnitApi.list();
      setUnits(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudieron cargar las unidades.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUnits();
  }, [fetchUnits]);

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
      is_active: unit.is_active,
    });
    setFormError(null);
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    setFormError(null);
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
      fetchUnits();
    } catch (e) {
      setFormError(e instanceof Error ? e.message : "No se pudo guardar la unidad.");
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
      fetchUnits();
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo eliminar la unidad.");
      setDeleteTarget(null);
    } finally {
      setDeleting(false);
    }
  };

  const activeCount = units.filter((u) => u.is_active).length;

  return (
    <>
      <PageMeta
        title="Academix | Unidades académicas"
        description="Gestión académica de la universidad"
      />
      <div className="space-y-6">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm font-medium text-brand-500">Universidad</p>
            <h1 className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
              Resumen académico
            </h1>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Una vista clara del alcance institucional de Academix.
            </p>
          </div>
          <Button onClick={openCreate} size="sm">
            <PlusIcon className="size-5" />
            Nueva unidad
          </Button>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {[
            { value: "1", label: "Universidad" },
            { value: String(units.length), label: "Unidades académicas" },
            { value: String(activeCount), label: "Activas" },
          ].map((metric) => (
            <div
              key={metric.label}
              className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]"
            >
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {metric.value}
              </p>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {metric.label}
              </p>
            </div>
          ))}
        </div>

        {error && (
          <div className="rounded-2xl border border-error-200 bg-error-50 px-5 py-4 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
            {error}
          </div>
        )}

        <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
          <div className="border-b border-gray-200 px-5 py-4 dark:border-gray-800">
            <h2 className="font-semibold text-gray-900 dark:text-white">
              Unidades académicas
            </h2>
          </div>
          <div className="overflow-x-auto">
            {loading ? (
              <div className="px-5 py-10 text-center text-sm text-gray-500 dark:text-gray-400">
                Cargando unidades…
              </div>
            ) : units.length === 0 ? (
              <div className="px-5 py-10 text-center text-sm text-gray-500 dark:text-gray-400">
                Aún no hay unidades registradas.
              </div>
            ) : (
              <table className="w-full min-w-[720px] text-left text-sm">
                <thead className="bg-gray-50 text-xs uppercase text-gray-500 dark:bg-white/[0.02] dark:text-gray-400">
                  <tr>
                    <th className="px-5 py-3">Código</th>
                    <th className="px-5 py-3">Nombre corto</th>
                    <th className="px-5 py-3">Nombre</th>
                    <th className="px-5 py-3">Estado</th>
                    <th className="px-5 py-3 text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {units.map((unit) => (
                    <tr key={unit.id} className="hover:bg-gray-50 dark:hover:bg-white/[0.02]">
                      <td className="px-5 py-4 font-medium text-gray-900 dark:text-white">
                        {unit.code}
                      </td>
                      <td className="px-5 py-4 text-gray-600 dark:text-gray-300">
                        {unit.short_name}
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
            <div>
              <Label htmlFor="unit-name">Nombre</Label>
              <Input
                id="unit-name"
                placeholder="Ej. Facultad de Ingeniería"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>
            <label className="flex cursor-pointer items-center gap-3">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) =>
                  setForm({ ...form, is_active: e.target.checked })
                }
                className="h-5 w-5 rounded border-gray-300 text-brand-500 focus:ring-brand-500/20"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-400">
                Unidad activa
              </span>
            </label>
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

      <Modal isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)}>
        <div className="p-6 sm:p-8">
          <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-full bg-error-50 text-error-500 dark:bg-error-500/10">
            <TrashBinIcon className="size-5" />
          </div>
          <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
            Eliminar unidad
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
    </>
  );
}
