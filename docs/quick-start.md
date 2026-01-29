# 🚀 Guide de Démarrage Rapide - CRM BTP

## Démarrage en 5 minutes

### 1. Prérequis

- Docker Desktop installé et en cours d'exécution
- Les ports 5173, 8000, 5432, et 6379 disponibles

### 2. Lancer l'application

```bash
# Copier les variables d'environnement
cp .env.example .env

# Démarrer tous les services
docker-compose up -d

# Attendre que tout démarre (30 secondes environ)
```

### 3. Accéder à l'application

- **Frontend** : http://localhost:5173
- **API Docs** : http://localhost:8000/docs
- **API Health** : http://localhost:8000/health

### 4. Vérifier le statut

```bash
docker-compose ps
```

Tous les services devraient être "Up".

## Arrêter l'application

```bash
docker-compose down
```

## Problème ?

```bash
# Voir les logs
docker-compose logs -f

# Redémarrer tout
docker-compose restart
```

## Plus d'infos

- [Installation détaillée](installation.md)
- [Plan d'implémentation](../README.md)
