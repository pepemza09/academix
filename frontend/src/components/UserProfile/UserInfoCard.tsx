import { useState } from "react";
import { useModal } from "../../hooks/useModal";
import { Modal } from "../ui/modal";
import Button from "../ui/button/Button";
import Input from "../form/input/InputField";
import Label from "../form/Label";
import { useAuth } from "../../context/AuthContext";
import { authApi } from "../../api/auth";
import { PencilIcon } from "../../icons";

export default function UserInfoCard() {
  const { isOpen, openModal, closeModal } = useModal();
  const { user } = useAuth();

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [saving, setSaving] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null);

  const resetPasswordForm = () => {
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setPasswordError(null);
    setPasswordSuccess(null);
  };

  const closeModalAndReset = () => {
    resetPasswordForm();
    closeModal();
  };

  const handleChangePassword = async () => {
    setPasswordError(null);
    setPasswordSuccess(null);

    if (!currentPassword) {
      setPasswordError("Debés ingresar tu contraseña actual.");
      return;
    }
    if (!newPassword || newPassword.length < 8) {
      setPasswordError("La nueva contraseña debe tener al menos 8 caracteres.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("Las contraseñas no coinciden.");
      return;
    }

    setSaving(true);
    try {
      await authApi.changePassword(currentPassword, newPassword);
      resetPasswordForm();
      setPasswordSuccess("Contraseña actualizada correctamente.");
    } catch (e) {
      setPasswordError(
        e instanceof Error ? e.message : "No se pudo cambiar la contraseña.",
      );
    } finally {
      setSaving(false);
    }
  };

  const displayName =
    user && (user.first_name || user.last_name)
      ? `${user.first_name} ${user.last_name}`.trim()
      : user?.username || "Usuario";

  return (
    <div className="p-5 border border-gray-200 rounded-2xl dark:border-gray-800 lg:p-6">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h4 className="text-lg font-semibold text-gray-800 dark:text-white/90 lg:mb-6">
            Información personal
          </h4>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:gap-7 2xl:gap-x-32">
            <div>
              <p className="mb-2 text-xs leading-normal text-gray-500 dark:text-gray-400">
                Nombre
              </p>
              <p className="text-sm font-medium text-gray-800 dark:text-white/90">
                {displayName}
              </p>
            </div>

            <div>
              <p className="mb-2 text-xs leading-normal text-gray-500 dark:text-gray-400">
                Usuario
              </p>
              <p className="text-sm font-medium text-gray-800 dark:text-white/90">
                @{user?.username}
              </p>
            </div>

            <div>
              <p className="mb-2 text-xs leading-normal text-gray-500 dark:text-gray-400">
                Correo electrónico
              </p>
              <p className="text-sm font-medium text-gray-800 dark:text-white/90">
                {user?.email || "Sin correo vinculado"}
              </p>
            </div>

            <div>
              <p className="mb-2 text-xs leading-normal text-gray-500 dark:text-gray-400">
                Cuenta
              </p>
              <p className="text-sm font-medium text-gray-800 dark:text-white/90">
                {user?.is_local ? "Local" : "Google"}
              </p>
            </div>
          </div>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={openModal}
          className="font-bold"
          startIcon={<PencilIcon className="size-5" />}
        >
          Editar
        </Button>
      </div>

      <Modal isOpen={isOpen} onClose={closeModal} className="max-w-[700px] m-4">
        <div className="no-scrollbar relative w-full max-w-[700px] overflow-y-auto rounded-3xl bg-white p-4 dark:bg-gray-900 lg:p-11">
          <div className="px-2 pr-14">
            <h4 className="mb-2 text-2xl font-semibold text-gray-800 dark:text-white/90">
              Editar información personal
            </h4>
            <p className="mb-6 text-sm text-gray-500 dark:text-gray-400 lg:mb-7">
              Actualizá tus datos para mantener tu perfil al día.
            </p>
          </div>
          <form
            className="flex flex-col"
            onSubmit={(e) => e.preventDefault()}
          >
            <div className="custom-scrollbar h-[450px] overflow-y-auto px-2 pb-3">
              <div>
                <h5 className="mb-5 text-lg font-medium text-gray-800 dark:text-white/90 lg:mb-6">
                  Datos de la cuenta
                </h5>

                <div className="grid grid-cols-1 gap-x-6 gap-y-5 lg:grid-cols-2">
                  <div>
                    <Label>Nombre</Label>
                    <Input type="text" value={displayName} disabled />
                  </div>

                  <div>
                    <Label>Usuario</Label>
                    <Input type="text" value={user?.username || ""} disabled />
                  </div>

                  <div className="col-span-2">
                    <Label>Correo electrónico</Label>
                    <Input type="text" value={user?.email || ""} disabled />
                  </div>
                </div>
              </div>

              {user?.is_local && (
                <div className="mt-7 border-t border-gray-200 pt-6 dark:border-gray-800">
                  <h5 className="mb-5 text-lg font-medium text-gray-800 dark:text-white/90">
                    Cambiar contraseña
                  </h5>

                  <div className="grid grid-cols-1 gap-x-6 gap-y-5">
                    <div className="col-span-2">
                      <Label>Contraseña actual</Label>
                      <Input
                        type="password"
                        placeholder="Ingresá tu contraseña actual"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                      />
                    </div>
                    <div className="col-span-2 lg:col-span-1">
                      <Label>Nueva contraseña</Label>
                      <Input
                        type="password"
                        placeholder="Mínimo 8 caracteres"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                      />
                    </div>
                    <div className="col-span-2 lg:col-span-1">
                      <Label>Confirmar nueva contraseña</Label>
                      <Input
                        type="password"
                        placeholder="Repetí la nueva contraseña"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                      />
                    </div>
                  </div>

                  {passwordError && (
                    <div className="mt-4 rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
                      {passwordError}
                    </div>
                  )}
                  {passwordSuccess && (
                    <div className="mt-4 rounded-lg border border-success-200 bg-success-50 px-4 py-3 text-sm text-success-600 dark:border-success-500/20 dark:bg-success-500/10 dark:text-success-400">
                      {passwordSuccess}
                    </div>
                  )}

                  <div className="mt-5 flex justify-end">
                    <Button
                      size="sm"
                      onClick={handleChangePassword}
                      disabled={saving}
                    >
                      {saving ? "Guardando…" : "Cambiar contraseña"}
                    </Button>
                  </div>
                </div>
              )}
            </div>
            <div className="flex items-center gap-3 px-2 mt-6 lg:justify-end">
              <Button size="sm" variant="outline" onClick={closeModalAndReset}>
                Cerrar
              </Button>
            </div>
          </form>
        </div>
      </Modal>
    </div>
  );
}
