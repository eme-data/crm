# Guide d'Installation - CRM BTP

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Docker** 24.0 ou supérieur ([Télécharger Docker Desktop](https://www.docker.com/products/docker-desktop/))
- **Docker Compose** 2.20 ou supérieur (inclus avec Docker Desktop)
- **Git** ([Télécharger Git](https://git-scm.com/downloads))

### Vérifier les installations

```bash
docker --version
docker-compose --version
git --version
```

## Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd crm
```

### 2. Configuration des variables d'environnement

Copiez le fichier d'exemple et configurez vos variables :

```bash
cp .env.example .env
```

Éditez le fichier `.env` et modifiez au minimum :

```env
POSTGRES_PASSWORD=votre_mot_de_passe_securise
SECRET_KEY=votre_cle_secrete_min_32_caracteres
```

> ⚠️ **Important** : En production, utilisez des mots de passe forts et uniques !

### 3. Lancer l'application

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs en temps réel
docker-compose logs -f
```

### 4. Vérifier que tout fonctionne

Ouvrez votre navigateur et accédez à :

- **Frontend** : [http://localhost:5173](http://localhost:5173)
- **API Backend** : [http://localhost:8000](http://localhost:8000)
- **Documentation API** : [http://localhost:8000/docs](http://localhost:8000/docs)

Vous devriez voir la page d'accueil avec les statuts des services.

## Commandes Utiles

### Gestion de Docker

```bash
# Démarrer les services
docker-compose up -d

# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes (⚠️ supprime les données)
docker-compose down -v

# Voir l'état des conteneurs
docker-compose ps

# Voir les logs
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Redémarrer un service
docker-compose restart backend

# Rebuild après modification du code
docker-compose build
docker-compose up -d
```

### Accéder aux conteneurs

```bash
# Accéder au conteneur backend
docker-compose exec backend bash

# Accéder à PostgreSQL
docker-compose exec postgres psql -U crm_user -d crm_btp

# Accéder au conteneur frontend
docker-compose exec frontend sh
```

### Base de données

```bash
# Voir les tables PostgreSQL
docker-compose exec postgres psql -U crm_user -d crm_btp -c "\dt"

# Exécuter une requête SQL
docker-compose exec postgres psql -U crm_user -d crm_btp -c "SELECT * FROM users;"

# Backup de la base de données
docker-compose exec postgres pg_dump -U crm_user crm_btp > backup.sql

# Restaurer un backup
docker-compose exec -T postgres psql -U crm_user crm_btp < backup.sql
```

## Migration de la base de données (à venir avec Alembic)

```bash
# Créer une nouvelle migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Appliquer les migrations
docker-compose exec backend alembic upgrade head

# Revenir à une version précédente
docker-compose exec backend alembic downgrade -1
```

## Développement

### Frontend

Les modifications dans `frontend/src/` sont automatiquement rechargées grâce au Hot Module Replacement de Vite.

### Backend

Le backend utilise `--reload` d'Uvicorn, donc les modifications Python sont automatiquement rechargées.

## Résolution de problèmes

### Le port 5173 est déjà utilisé

Modifiez le port dans `docker-compose.yml` :

```yaml
frontend:
  ports:
    - "3000:5173"  # Utiliser le port 3000 au lieu de 5173
```

### Le port 8000 est déjà utilisé

Modifiez le port dans `docker-compose.yml` :

```yaml
backend:
  ports:
    - "8001:8000"  # Utiliser le port 8001 au lieu de 8000
```

### Erreur de connexion à la base de données

1. Vérifiez que PostgreSQL est bien démarré :
   ```bash
   docker-compose ps postgres
   ```

2. Vérifiez les logs :
   ```bash
   docker-compose logs postgres
   ```

3. Recréez le conteneur :
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Les modules npm ne sont pas installés

```bash
# Rebuild le conteneur frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Réinitialiser complètement le projet

```bash
# ⚠️ Attention : cela supprime TOUTES les données
docker-compose down -v
docker-compose build
docker-compose up -d
```

## Structure des conteneurs

L'application utilise 4 conteneurs Docker :

1. **postgres** - Base de données PostgreSQL
   - Port : 5432
   - Volume : `postgres_data` (données persistantes)

2. **redis** - Cache Redis
   - Port : 6379
   - Volume : `redis_data` (données persistantes)

3. **backend** - API FastAPI
   - Port : 8000
   - Volume : `./backend` monté pour le hot-reload

4. **frontend** - Application React
   - Port : 5173
   - Volume : `./frontend` monté pour le hot-reload

## Production

Pour déployer en production :

1. Créez un fichier `docker-compose.prod.yml`
2. Modifiez les variables d'environnement pour la production
3. Configurez Nginx pour le reverse proxy
4. Utilisez des secrets Docker au lieu de `.env`
5. Activez HTTPS avec Let's Encrypt

Voir la documentation détaillée dans `docs/deployment.md` (à venir).

## Support

Pour toute question :
- Consultez la [documentation complète](../implementation_plan.md)
- Ouvrez une issue sur le repository
- Contactez l'équipe de développement

## Prochaines étapes

✅ **Phase 1 complétée** - Infrastructure Docker

Prochaines phases :
- Phase 2 : Backend Core (Authentification, API Catalogue, Devis/Factures)
- Phase 3 : Frontend UI (Interfaces utilisateur complètes)
- Phase 4 : Fonctionnalités avancées (PDF, Stats, Multi-devises)
- Phase 5 : Tests & Déploiement
