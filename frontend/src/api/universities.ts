import { api } from "./client";

export interface University {
  id: number;
  name: string;
  short_name: string;
  is_active: boolean;
}

export type UniversityPayload = Omit<University, "id">;

export const universityApi = {
  list: () => api.get<University[]>("/universities/"),
  create: (data: UniversityPayload) =>
    api.post<University>("/universities/", data),
  update: (id: number, data: UniversityPayload) =>
    api.patch<University>(`/universities/${id}/`, data),
  remove: (id: number) => api.delete<void>(`/universities/${id}/`),
};
