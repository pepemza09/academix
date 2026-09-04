import { api } from "./client";

export const PERIOD_OPTIONS = [
  { value: "1Q", label: "1er Cuatrimestre" },
  { value: "2Q", label: "2do Cuatrimestre" },
  { value: "1B", label: "1er Bimestre" },
  { value: "2B", label: "2do Bimestre" },
  { value: "3B", label: "3er Bimestre" },
  { value: "4B", label: "4to Bimestre" },
  { value: "AN", label: "Anual" },
] as const;

export interface Subject {
  id: number;
  code: string;
  name: string;
  year: number;
  period: string;
  period_label: string;
  study_area: number;
  study_area_name: string;
  study_plan_code: string;
  study_plan_title: string;
  career_name: string;
  career_code: string;
  duration_years: number;
  nomenclador?: number | null;
  nomenclador_extra?: string;
  nomenclador_label?: string | null;
  is_active: boolean;
}

export interface SubjectPayload {
  code: string;
  name: string;
  year: number;
  period: string;
  study_area: number;
  nomenclador?: number | null;
  nomenclador_extra?: string;
  is_active: boolean;
}

export const subjectApi = {
  list: () => api.get<Subject[]>("/subjects/"),
  create: (data: SubjectPayload) => api.post<Subject>("/subjects/", data),
  update: (id: number, data: SubjectPayload) =>
    api.patch<Subject>(`/subjects/${id}/`, data),
  remove: (id: number) => api.delete<void>(`/subjects/${id}/`),
};
