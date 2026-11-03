import { useAuth } from "../context/AuthContext";

/**
 * Permisos cosméticos por rol (la autorización real vive en el backend):
 *
 * - viewer: solo lectura (no ve botones de crear, editar ni eliminar).
 * - editor: crea y edita (no ve el botón de eliminar).
 * - admin : todo.
 *
 * Mientras no se resuelva el rol (`ready === false`) se ocultan los
 * controles de escritura para evitar un flash de botones que el backend
 * rechazaría (mínimo privilegio visual).
 */
export function usePermissions() {
  const { user, loading } = useAuth();
  const role = user?.role;
  const ready = !loading && !!user && !!role;

  return {
    role,
    ready,
    canWrite: ready && (role === "admin" || role === "editor"),
    canDelete: ready && role === "admin",
  };
}
