/**
 * Service pour les articles
 */

import api from '../lib/api';

export interface Article {
    id: string;
    code: string;
    name: string;
    description?: string;
    unit: string;
    total_price: number;
    material_cost: number;
    labor_cost: number;
    margin: number;
    overhead: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export const articlesService = {
    /**
     * Lister les articles
     */
    async list(params?: {
        skip?: number;
        limit?: number;
        active_only?: boolean;
        search?: string;
    }): Promise<Article[]> {
        const response = await api.get<Article[]>('/api/articles/', { params });
        return response.data;
    },

    /**
     * Récupérer un article
     */
    async get(id: string): Promise<Article> {
        const response = await api.get<Article>(`/api/articles/${id}`);
        return response.data;
    },

    /**
     * Supprimer un article
     */
    async delete(id: string): Promise<void> {
        await api.delete(`/api/articles/${id}`);
    },

    /**
     * Recalculer les prix d'un article
     */
    async recalculate(id: string): Promise<Article> {
        const response = await api.post<Article>(`/api/articles/${id}/recalculate`);
        return response.data;
    },
};
