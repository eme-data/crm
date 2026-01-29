/**
 * Service pour les matériaux
 */

import api from '../lib/api';

export interface Material {
    id: string;
    code: string;
    name_fr: string;
    name_ro?: string;
    description?: string;
    unit: string;
    price_eur: number;
    price_lei?: number;
    price_date: string;
    supplier?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface MaterialCreate {
    code: string;
    name_fr: string;
    name_ro?: string;
    description?: string;
    unit: string;
    price_eur: number;
    price_lei?: number;
    supplier?: string;
}

export interface MaterialUpdate {
    code?: string;
    name_fr?: string;
    name_ro?: string;
    description?: string;
    unit?: string;
    price_eur?: number;
    price_lei?: number;
    supplier?: string;
    is_active?: boolean;
}

export const materialsService = {
    /**
     * Lister les matériaux
     */
    async list(params?: {
        skip?: number;
        limit?: number;
        active_only?: boolean;
        search?: string;
    }): Promise<Material[]> {
        const response = await api.get<Material[]>('/api/materials/', { params });
        return response.data;
    },

    /**
     * Récupérer un matériau
     */
    async get(id: string): Promise<Material> {
        const response = await api.get<Material>(`/api/materials/${id}`);
        return response.data;
    },

    /**
     * Créer un matériau
     */
    async create(data: MaterialCreate): Promise<Material> {
        const response = await api.post<Material>('/api/materials/', data);
        return response.data;
    },

    /**
     * Mettre à jour un matériau
     */
    async update(id: string, data: MaterialUpdate): Promise<Material> {
        const response = await api.put<Material>(`/api/materials/${id}`, data);
        return response.data;
    },

    /**
     * Supprimer un matériau
     */
    async delete(id: string): Promise<void> {
        await api.delete(`/api/materials/${id}`);
    },
};
