/**
 * Service pour les services
 */

import api from '../lib/api';

export interface Service {
    id: string;
    code: string;
    name: string;
    description?: string;
    unit: string;
    price_net: number;
    price_gross: number;
    margin: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export const servicesService = {
    /**
     * Lister les services
     */
    async list(params?: {
        skip?: number;
        limit?: number;
        active_only?: boolean;
        search?: string;
    }): Promise<Service[]> {
        const response = await api.get<Service[]>('/api/services/', { params });
        return response.data;
    },

    /**
     * Récupérer un service
     */
    async get(id: string): Promise<Service> {
        const response = await api.get<Service>(`/api/services/${id}`);
        return response.data;
    },

    /**
     * Supprimer un service
     */
    async delete(id: string): Promise<void> {
        await api.delete(`/api/services/${id}`);
    },
};
