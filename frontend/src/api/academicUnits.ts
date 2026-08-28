import { api } from "./client";

export interface AcademicUnit {
  id: number;
  code: string;
  short_name: string;
  name: string;
  university: number;
  university_name: string;
  is_active: boolean;
}

export type AcademicUnitPayload = Pick<
  AcademicUnit,
  "code" | "short_name" | "name" | "university" | "is_active"
>;

export const academicUnitApi = {
  list: () => api.get<AcademicUnit[]>("/academic-units/"),
  create: (data: AcademicUnitPayload) =>
    api.post<AcademicUnit>("/academic-units/", data),
  update: (id: number, data: AcademicUnitPayload) =>
    api.patch<AcademicUnit>(`/academic-units/${id}/`, data),
  remove: (id: number) => api.delete<void>(`/academic-units/${id}/`),
};
