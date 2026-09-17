import { api } from "./client";

export interface FormOptions {
  universities: Array<{
    id: number;
    name: string;
    short_name: string;
    is_active: boolean;
    academic_unit_count: number;
  }>;
  academic_units: Array<{
    id: number;
    code: string;
    short_name: string;
    name: string;
    university: number;
    university_name: string;
    campus_count: number;
    is_active: boolean;
  }>;
  campuses: Array<{
    id: number;
    code: string;
    name: string;
    academic_unit: number;
    academic_unit_name: string;
    is_active: boolean;
  }>;
  careers: Array<{
    id: number;
    code: string;
    short_name: string;
    name: string;
    academic_unit: number;
    academic_unit_name: string;
    campuses: number[];
    campus_count: number;
    campus_details: Array<{
      id: number;
      code: string;
      name: string;
    }>;
    is_active: boolean;
  }>;
  study_plans: Array<{
    id: number;
    code: string;
    title: string;
    intermediate_title: string;
    duration_years: number;
    career: number;
    career_name: string;
    career_code: string;
    is_active: boolean;
    is_current: boolean;
  }>;
  study_areas: Array<{
    id: number;
    name: string;
    study_plan: number;
    study_plan_code: string;
    study_plan_title: string;
    career_name: string;
    career_code: string;
    is_active: boolean;
  }>;
  subjects: Array<{
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
  }>;
  nomencladores: Array<{
    id: number;
    discipline: string;
    subdiscipline: string;
    specialty: string;
    is_active: boolean;
  }>;
}

export const formOptionsApi = {
  list: (signal?: AbortSignal) =>
    api.get<FormOptions>("/form-options/", signal),
};
