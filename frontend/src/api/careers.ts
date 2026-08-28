import { api } from "./client";

export interface Career {
  id: number;
  code: string;
  short_name: string;
  name: string;
  academic_unit: number;
  academic_unit_name: string;
  campuses: number[];
  campus_count: number;
  campus_details: { id: number; code: string; name: string }[];
  is_active: boolean;
}

export interface CareerPayload {
  code: string;
  short_name: string;
  name: string;
  academic_unit: number;
  campuses: number[];
  is_active: boolean;
}

export const careerApi = {
  list: () => api.get<Career[]>("/careers/"),
  create: (data: CareerPayload) => api.post<Career>("/careers/", data),
  update: (id: number, data: CareerPayload) =>
    api.patch<Career>(`/careers/${id}/`, data),
  remove: (id: number) => api.delete<void>(`/careers/${id}/`),
};
