import { api } from "./client";

export interface Campus {
  id: number;
  code: string;
  name: string;
  academic_unit: number;
  academic_unit_name: string;
  is_active: boolean;
}

export type CampusPayload = Pick<
  Campus,
  "code" | "name" | "academic_unit" | "is_active"
>;

export const campusApi = {
  list: () => api.get<Campus[]>("/campuses/"),
  create: (data: CampusPayload) => api.post<Campus>("/campuses/", data),
  update: (id: number, data: CampusPayload) =>
    api.patch<Campus>(`/campuses/${id}/`, data),
  remove: (id: number) => api.delete<void>(`/campuses/${id}/`),
};
