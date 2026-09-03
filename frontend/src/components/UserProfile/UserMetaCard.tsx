import { useRef, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { authApi } from "../../api/auth";
import Button from "../ui/button/Button";
import { PencilIcon } from "../../icons";

export default function UserMetaCard() {
  const { user, refreshUser } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const displayName =
    user && (user.first_name || user.last_name)
      ? `${user.first_name} ${user.last_name}`.trim()
      : user?.username || "Usuario";

  const avatarSrc = preview || user?.avatar || undefined;

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setError(null);
    setPreview(URL.createObjectURL(file));
    setUploading(true);
    try {
      await authApi.uploadAvatar(file);
      await refreshUser();
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "No se pudo subir la foto de perfil.",
      );
    } finally {
      setPreview(null);
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="p-5 border border-gray-200 rounded-2xl dark:border-gray-800 lg:p-6">
      <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex flex-col items-center w-full gap-6 xl:flex-row">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="relative w-20 h-20 overflow-hidden border border-gray-200 rounded-full dark:border-gray-800 group shrink-0"
            title="Cambiar foto de perfil"
          >
            {avatarSrc ? (
              <img
                src={avatarSrc}
                alt={displayName}
                className="object-cover w-full h-full"
              />
            ) : (
              <span className="flex items-center justify-center w-full h-full text-2xl font-semibold text-white bg-brand-500">
                {displayName.charAt(0).toUpperCase()}
              </span>
            )}
            <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity">
              {uploading ? "Subiendo…" : "Cambiar"}
            </span>
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
          />

          <div className="order-3 xl:order-2">
            <h4 className="mb-2 text-lg font-semibold text-center text-gray-800 dark:text-white/90 xl:text-left">
              {displayName}
            </h4>
            <div className="flex flex-col items-center gap-1 text-center xl:flex-row xl:gap-3 xl:text-left">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                @{user?.username}
              </p>
              <div className="hidden h-3.5 w-px bg-gray-300 dark:bg-gray-700 xl:block"></div>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {user?.email || "Sin correo vinculado"}
              </p>
            </div>
          </div>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="font-bold"
          startIcon={<PencilIcon className="size-5" />}
        >
          {uploading ? "Subiendo…" : "Cambiar foto"}
        </Button>
      </div>

      {error && (
        <p className="mt-4 rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
          {error}
        </p>
      )}
    </div>
  );
}
