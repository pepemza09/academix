import { api } from "./client";

export interface Nomenclador {
  id: number;
  discipline: string;
  subdiscipline: string;
  specialty: string;
  is_active: boolean;
}

export type NomencladorPayload = Omit<Nomenclador, "id">;

export interface NomencladorView {
  value: number;
  label: string;
}

export function nomencladorLabel(n: {
  discipline: string;
  subdiscipline: string;
  specialty: string;
}): string {
  return `${n.discipline} / ${n.subdiscipline} / ${n.specialty}`;
}

export const nomencladorApi = {
  list: () => api.get<Nomenclador[]>("/nomencladores/"),
  create: (data: NomencladorPayload) =>
    api.post<Nomenclador>("/nomencladores/", data),
  update: (id: number, data: NomencladorPayload) =>
    api.patch<Nomenclador>(`/nomencladores/${id}/`, data),
  remove: (id: number) => api.delete<void>(`/nomencladores/${id}/`),
};
