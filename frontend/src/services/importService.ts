/**
 * Service d'import Excel
 */

import api from '../lib/api';

export interface ImportStats {
    created: number;
    updated: number;
    errors: number;
    total: number;
}

export interface ImportResponse {
    message: string;
    statistics: ImportStats;
    file: string;
    sheet: string;
}

export interface ExcelStructure {
    filename: string;
    sheets: Record<string, string[]>;
}

export const importService = {
    /**
     * Détecter la structure d'un fichier Excel
     */
    async detectStructure(file: File): Promise<ExcelStructure> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post<ExcelStructure>(
            '/api/import/excel/detect-structure',
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }
        );
        return response.data;
    },

    /**
     * Importer des matériaux depuis Excel
     */
    async importMaterials(file: File, sheetName: string): Promise<ImportResponse> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post<ImportResponse>(
            `/api/import/excel/materials?sheet_name=${encodeURIComponent(sheetName)}`,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }
        );
        return response.data;
    },

    /**
     * Importer des services depuis Excel
     */
    async importServices(file: File, sheetName: string): Promise<ImportResponse> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post<ImportResponse>(
            `/api/import/excel/services?sheet_name=${encodeURIComponent(sheetName)}`,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }
        );
        return response.data;
    },
};
