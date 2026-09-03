import { api } from "./client";

export interface User {
  id: number;
  username: string;
  email: string;
  is_local: boolean;
  auth_provider: "local" | "google";
  avatar: string | null;
  first_name: string;
  last_name: string;
}

export const authApi = {
  me: () => api.get<User>("/auth/me/"),
  login: (username: string, password: string) =>
    api.post<User>("/auth/login/", { username, password }),
  logout: () => api.post<void>("/auth/logout/", {}),
  changePassword: (currentPassword: string, newPassword: string) =>
    api.post<{ status: string; detail: string }>("/auth/change-password/", {
      current_password: currentPassword,
      new_password: newPassword,
    }),
  uploadAvatar: (file: File) => {
    const formData = new FormData();
    formData.append("avatar", file);
    return api.upload<{ status: string; detail: string; avatar: string }>(
      "/auth/upload-avatar/",
      formData,
    );
  },
};

export const GOOGLE_LOGIN_URL = "/auth/login/google-oauth2/";
