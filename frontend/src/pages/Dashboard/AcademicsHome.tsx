import { useCallback, useEffect, useState } from "react";
import PageMeta from "../../components/common/PageMeta";
import Badge from "../../components/ui/badge/Badge";
import { AcademicUnit, academicUnitApi } from "../../api/academicUnits";

export default function AcademicsHome() {
  const [units, setUnits] = useState<AcademicUnit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUnits = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await academicUnitApi.list();
      setUnits(data);
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
    fetchUnits();
  }, [fetchUnits]);

  const activeCount = units.filter((u) => u.is_active).length;

  return (
    <>
      <PageMeta
        title="Academix | Resumen general"
        description="Resumen académico de la universidad"
      />
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
          Resumen general
        </h1>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {[
            { value: String(units.length), label: "Unidades académicas" },
            { value: String(activeCount), label: "Activas" },
            {
              value: String(units.length - activeCount),
              label: "Inactivas",
            },
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
                Cargando unidades académicas…
              </div>
            ) : units.length === 0 ? (
              <div className="px-5 py-10 text-center text-sm text-gray-500 dark:text-gray-400">
                Aún no hay unidades académicas registradas.
              </div>
            ) : (
              <table className="w-full min-w-[720px] text-left text-sm">
                <thead className="bg-gray-50 text-xs uppercase text-gray-500 dark:bg-white/[0.02] dark:text-gray-400">
                  <tr>
                    <th className="px-5 py-3">Universidad</th>
                    <th className="px-5 py-3">Código</th>
                    <th className="px-5 py-3">Nombre</th>
                    <th className="px-5 py-3">Estado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {units.map((unit) => (
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
                        {unit.name}
                      </td>
                      <td className="px-5 py-4">
                        {unit.is_active ? (
                          <Badge color="success">Activa</Badge>
                        ) : (
                          <Badge color="warning">Inactiva</Badge>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
