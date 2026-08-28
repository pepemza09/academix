import { api } from "./client";

export interface StudyPlan {
  id: number;
  code: string;
  title: string;
  career: number;
  career_name: string;
  career_code: string;
  is_active: boolean;
  is_current: boolean;
}

export interface StudyPlanPayload {
  code: string;
  title: string;
  career: number;
  is_active: boolean;
  is_current: boolean;
}

export const studyPlanApi = {
  list: () => api.get<StudyPlan[]>("/study-plans/"),
  create: (data: StudyPlanPayload) => api.post<StudyPlan>("/study-plans/", data),
  update: (id: number, data: StudyPlanPayload) =>
    api.patch<StudyPlan>(`/study-plans/${id}/`, data),
  remove: (id: number) => api.delete<void>(`/study-plans/${id}/`),
};
