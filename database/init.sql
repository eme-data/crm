-- Script d'initialisation de la base de données CRM BTP
-- Exécuté automatiquement au premier démarrage du container PostgreSQL

-- Créer les extensions nécessaires
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table pour stocker les informations de version
CREATE TABLE IF NOT EXISTS schema_version (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insérer la version initiale
INSERT INTO schema_version (version) VALUES ('1.0.0')
ON CONFLICT (version) DO NOTHING;

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Base de données CRM BTP initialisée avec succès!';
END $$;
