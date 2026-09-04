import { useEffect, useState } from "react";
import { Link } from "react-router";
import PageMeta from "../../components/common/PageMeta";
import Button from "../../components/ui/button/Button";
import Badge from "../../components/ui/badge/Badge";
import { DocsIcon } from "../../icons";
import { nomencladorApi } from "../../api/nomencladores";

export default function ConfiguracionesIndex() {
  const [nomencladorCount, setNomencladorCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    nomencladorApi
      .list()
      .then((data) => setNomencladorCount(data.length))
      .catch(() => setNomencladorCount(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageMeta
        title="Academix | Configuraciones"
        description="Panel de configuraciones del sistema"
      />

      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
            Configuración del sistema
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Administra las tablas maestras, nomencladores y parámetros globales de Academix.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Card: Nomenclador */}
          <div className="flex flex-col justify-between rounded-2xl border border-gray-200 bg-white p-6 shadow-theme-xs transition-all hover:border-brand-300 dark:border-gray-800 dark:bg-white/[0.03] dark:hover:border-brand-800">
            <div>
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-50 text-brand-500 dark:bg-brand-500/10">
                    <DocsIcon className="size-5" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Nomenclador
                  </h3>
                </div>
                <Badge color="info">Oficial</Badge>
              </div>

              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Clasificación de disciplinas, subdisciplinas y especialidades académicas para asignar a las materias.
              </p>

              <div className="mt-4 flex items-center gap-2 text-xs font-medium text-gray-600 dark:text-gray-300">
                <span className="inline-block h-2 w-2 rounded-full bg-success-500"></span>
                {loading
                  ? "Cargando registros…"
                  : nomencladorCount !== null
                    ? `${nomencladorCount} registros cargados`
                    : "Tabla maestra"}
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-gray-100 dark:border-gray-800">
              <Link to="/configuraciones/nomenclador">
                <Button className="w-full justify-center">
                  Gestionar Nomenclador
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
