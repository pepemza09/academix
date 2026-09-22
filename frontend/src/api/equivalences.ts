import { api } from "./client";

export interface EquivalenceSubjectRef {
  id: number;
  code: string;
  name: string;
  study_plan: number;
  study_plan_code: string;
  study_plan_title: string;
  career_name: string;
  career_code: string;
}

export interface Equivalence {
  id: number;
  new_subjects: number[];
  old_subjects: number[];
  new_details: EquivalenceSubjectRef[];
  old_details: EquivalenceSubjectRef[];
  rule_text: string;
  is_active: boolean;
}

export interface EquivalencePayload {
  new_subjects: number[];
  old_subjects: number[];
  rule_text: string;
  is_active: boolean;
}

export const equivalenceApi = {
  list: (signal?: AbortSignal) =>
    api.get<Equivalence[]>("/equivalences/", signal),
  create: (data: EquivalencePayload) =>
    api.post<Equivalence>("/equivalences/", data),
  update: (id: number, data: EquivalencePayload) =>
    api.patch<Equivalence>(`/equivalences/${id}/`, data),
  remove: (id: number) => api.delete<void>(`/equivalences/${id}/`),
};
