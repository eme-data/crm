/**
 * Service d'authentification
 */

import api from '../lib/api';

export interface LoginRequest {
    email: string;
    password: string;
}

export interface User {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
    is_active: boolean;
    created_at: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
    user: User;
}

export const authService = {
    /**
     * Se connecter
     */
    async login(credentials: LoginRequest): Promise<LoginResponse> {
        const response = await api.post<LoginResponse>('/api/auth/login', credentials);

        // Stocker le token et l'utilisateur
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));

        return response.data;
    },

    /**
     * Se déconnecter
     */
    async logout(): Promise<void> {
        try {
            await api.post('/api/auth/logout');
        } finally {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
        }
    },

    /**
     * Récupérer l'utilisateur connecté
     */
    async getCurrentUser(): Promise<User> {
        const response = await api.get<User>('/api/auth/me');
        localStorage.setItem('user', JSON.stringify(response.data));
        return response.data;
    },

    /**
     * Vérifier si l'utilisateur est connecté
     */
    isAuthenticated(): boolean {
        return !!localStorage.getItem('access_token');
    },

    /**
     * Récupérer l'utilisateur du localStorage
     */
    getStoredUser(): User | null {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    },
};
