import { api } from "./client";

export interface StudyArea {
  id: number;
  name: string;
  study_plan: number;
  study_plan_code: string;
  study_plan_title: string;
  career_name: string;
  career_code: string;
  is_active: boolean;
}

export interface StudyAreaPayload {
  name: string;
  study_plan: number;
  is_active: boolean;
}

export const studyAreaApi = {
  list: () => api.get<StudyArea[]>("/study-areas/"),
  create: (data: StudyAreaPayload) => api.post<StudyArea>("/study-areas/", data),
  update: (id: number, data: StudyAreaPayload) =>
    api.patch<StudyArea>(`/study-areas/${id}/`, data),
  remove: (id: number) => api.delete<void>(`/study-areas/${id}/`),
};
