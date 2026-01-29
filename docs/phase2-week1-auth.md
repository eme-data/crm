# Phase 2 - Semaine 1 : Authentification ✅

## Résumé

Module d'authentification complet implémenté avec Alembic, JWT, et gestion des rôles.

## Ce qui a été créé

### 🗄️ Migrations de Base de Données (Alembic)

**Fichiers créés :**
- `backend/alembic.ini` - Configuration Alembic
- `backend/alembic/env.py` - Environnement de migration
- `backend/alembic/script.py.mako` - Template de migration
- `backend/alembic/versions/001_create_users_table.py` - Migration users table

**Commande pour appliquer :**
```bash
docker-compose exec backend alembic upgrade head
```

### 🔐 Authentification JWT

**Schémas Pydantic (`app/schemas/user.py`) :**
- `UserBase` - Schéma de base
- `UserCreate` - Création d'utilisateur
- `UserUpdate` - Mise à jour
- `User` - Retour API
- `Token` - Token JWT
- `LoginRequest` - Requête de login
- `LoginResponse` - Réponse de login

**Service (`app/services/auth_service.py`) :**
- `authenticate_user()` - Vérifier email/password
- `create_user()` - Créer un utilisateur
- `login()` - Connexion avec token JWT

**Dependencies (`app/api/dependencies.py`) :**
- `get_current_user()` - Récupérer l'utilisateur du token
- `get_current_active_admin()` - Vérifier si admin

### 📡 API Routes

**Endpoints (`app/api/auth.py`) :**

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| POST | `/api/auth/register` | ❌ | Créer un compte |
| POST | `/api/auth/login` | ❌ | Se connecter |
| GET | `/api/auth/me` | ✅ | Info utilisateur actuel |
| POST | `/api/auth/logout` | ✅ | Se déconnecter |

### 👤 Modèle User

**Champs :**
- `id` (UUID) - Identifiant unique
- `email` (String, unique) - Email de connexion
- `password_hash` (String) - Mot de passe hashé (bcrypt)
- `first_name` (String) - Prénom
- `last_name` (String) - Nom
- `role` (Enum) - Rôle utilisateur
- `is_active` (Boolean) - Compte actif
- `created_at` / `updated_at` (String) - Timestamps

**Rôles disponibles :**
- **admin** - Accès complet
- **commercial** - Gestion devis/clients
- **gestionnaire** - Lecture seule
- **comptable** - Gestion factures

### 🛠️ Utilitaires

**Script Admin (`app/create_admin.py`) :**
- Crée un utilisateur admin par défaut
- Email: `admin@crm-btp.com`
- Password: `Admin123!`

**Commande :**
```bash
docker-compose exec backend python app/create_admin.py
```

## Tests

Voir le guide complet : [docs/test-authentication.md](test-authentication.md)

### Quick Test

```bash
# 1. Appliquer les migrations
docker-compose exec backend alembic upgrade head

# 2. Créer l'admin
docker-compose exec backend python app/create_admin.py

# 3. Tester dans Swagger
# Ouvrir http://localhost:8000/docs
# POST /api/auth/login avec admin@crm-btp.com / Admin123!
```

## Fichiers Modifiés

### Nouveaux fichiers (15)

1. `backend/alembic.ini`
2. `backend/alembic/env.py`
3. `backend/alembic/script.py.mako`
4. `backend/alembic/versions/001_create_users_table.py`
5. `backend/app/schemas/__init__.py`
6. `backend/app/schemas/user.py`
7. `backend/app/services/__init__.py`
8. `backend/app/services/auth_service.py`
9. `backend/app/api/__init__.py`
10. `backend/app/api/auth.py`
11. `backend/app/api/dependencies.py`
12. `backend/app/create_admin.py`
13. `docs/test-authentication.md`

### Fichiers modifiés (2)

1. `backend/app/main.py` - Enregistrement du router auth
2. `task.md` - Mise à jour progression

## Métriques

- **Fichiers créés** : 15
- **Lignes de code** : ~600
- **Endpoints API** : 4
- **Temps d'implémentation** : Semaine 1

## Sécurité

✅ **Implémenté :**
- Hachage bcrypt des mots de passe
- JWT avec expiration configurable (30 min par défaut)
- Validation des tokens
- Gestion des rôles
- Protection des routes sensibles
- Validation Pydantic des entrées

⚠️ **À améliorer pour la production :**
- Blacklist des tokens révoqués (Redis)
- Rate limiting sur les tentatives de login
- 2FA (Two-Factor Authentication)
- Password reset par email
- Logs des tentatives de connexion

## Prochaines Étapes

### Phase 2 - Semaine 2 : Module Catalogue

Objectifs :
- [ ] Modèles : Materials, Articles, Compositions, Services
- [ ] Migrations Alembic pour ces tables
- [ ] CRUD APIs pour chaque entité
- [ ] Import Excel de la matrice de prix
- [ ] Calculs automatiques de prix

**Estimation** : 1 semaine | Budget : 1200€

---

**✅ Semaine 1 complétée - Authentification fonctionnelle !**
