import { api } from "./client";

export interface User {
  id: number;
  username: string;
  email: string;
}

export const authApi = {
  me: () => api.get<User>("/auth/me/"),
  login: (username: string, password: string) =>
    api.post<User>("/auth/login/", { username, password }),
  logout: () => api.post<void>("/auth/logout/", {}),
};

export const GOOGLE_LOGIN_URL = "/auth/login/google-oauth2/";
