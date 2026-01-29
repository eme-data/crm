# Guide de Test - Module d'Authentification

## Prérequis

L'application doit être démarrée avec Docker Compose :

```bash
docker-compose up -d
```

## Étape 1 : Appliquer les migrations

```bash
# Appliquer la migration pour créer la table users
docker-compose exec backend alembic upgrade head
```

Vous devriez voir :
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Create users table
```

## Étape 2 : Créer un utilisateur administrateur

```bash
# Créer l'admin par défaut
docker-compose exec backend python app/create_admin.py
```

Vous devriez voir :
```
============================================================
✅ Utilisateur administrateur créé avec succès!
============================================================
Email:        admin@crm-btp.com
Mot de passe: Admin123!
============================================================
⚠️  IMPORTANT: Changez ce mot de passe après votre première connexion!
============================================================
```

## Étape 3 : Tester les endpoints d'authentification

### Option A : Via Swagger UI (Recommandé)

1. Ouvrez http://localhost:8000/docs

2. Vous verrez les nouveaux endpoints sous "Authentication":
   - POST `/api/auth/register`
   - POST `/api/auth/login`
   - GET `/api/auth/me`
   - POST `/api/auth/logout`

3. **Tester le login** :
   - Cliquez sur `POST /api/auth/login`
   - Cliquez sur "Try it out"
   - Entrez :
     ```json
     {
       "email": "admin@crm-btp.com",
       "password": "Admin123!"
     }
     ```
   - Cliquez sur "Execute"

4. **Résultat attendu** (Status 200):
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer",
     "user": {
       "email": "admin@crm-btp.com",
       "first_name": "Admin",
       "last_name": "CRM BTP",
       "role": "admin",
       "id": "...",
       "is_active": true,
       "created_at": "..."
     }
   }
   ```

5. **Copier le token** et l'utiliser pour les requêtes authentifiées :
   - Cliquez sur le bouton "Authorize" en haut de Swagger
   - Collez le token (juste la valeur, sans "Bearer")
   - Cliquez "Authorize"

6. **Tester GET /api/auth/me** :
   - Cliquez sur `GET /api/auth/me`
   - "Try it out" → "Execute"
   - Devrait retourner vos infos utilisateur

### Option B : Via curl (Ligne de commande)

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@crm-btp.com",
    "password": "Admin123!"
  }'

# Copier le access_token de la réponse

# 2. Récupérer le profil (remplacer YOUR_TOKEN)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Créer un nouvel utilisateur (en tant qu'admin)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "email": "commercial@crm-btp.com",
    "password": "Commercial123!",
    "first_name": "Jean",
    "last_name": "Dupont",
    "role": "commercial"
  }'
```

### Option C : Via Python (Requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "email": "admin@crm-btp.com",
        "password": "Admin123!"
    }
)

data = response.json()
token = data["access_token"]
print(f"Token: {token[:50]}...")

# Get current user
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    f"{BASE_URL}/api/auth/me",
    headers=headers
)

user = response.json()
print(f"User: {user['first_name']} {user['last_name']} ({user['role']})")
```

## Étape 4 : Tests de sécurité

### Test 1 : Login avec mauvais mot de passe

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@crm-btp.com",
    "password": "WrongPassword"
  }'
```

**Attendu**: Status 401, message "Email ou mot de passe incorrect"

### Test 2 : Accès à /me sans token

```bash
curl -X GET http://localhost:8000/api/auth/me
```

**Attendu**: Status 401, message "Not authenticated"

### Test 3 : Accès avec token invalide

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer invalid_token_here"
```

**Attendu**: Status 401, message "Impossible de valider les identifiants"

### Test 4 : Créer un utilisateur avec email existant

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@crm-btp.com",
    "password": "Test123!",
    "first_name": "Test",
    "last_name": "User",
    "role": "commercial"
  }'
```

**Attendu**: Status 400, message "Un utilisateur avec cet email existe déjà"

## Étape 5 : Vérifier la base de données

```bash
# Se connecter à PostgreSQL
docker-compose exec postgres psql -U crm_user -d crm_btp

# Lister les tables
\dt

# Voir les utilisateurs
SELECT email, first_name, last_name, role, is_active FROM users;

# Quitter
\q
```

## Résumé des Endpoints Disponibles

| Méthode | Endpoint | Auth Required | Description |
|---------|----------|---------------|-------------|
| POST | `/api/auth/register` | ❌ | Créer un compte |
| POST | `/api/auth/login` | ❌ | Se connecter |
| GET | `/api/auth/me` | ✅ | Info utilisateur actuel |
| POST | `/api/auth/logout` | ✅ | Se déconnecter |

## Rôles Disponibles

- **admin** - Accès complet, gestion utilisateurs
- **commercial** - Création devis/factures, gestion clients
- **gestionnaire** - Lecture seule, reporting
- **comptable** - Gestion factures, exports

## Troubleshooting

### Erreur "Table users does not exist"

Solution :
```bash
docker-compose exec backend alembic upgrade head
```

### Erreur "No admin user found"

Solution :
```bash
docker-compose exec backend python app/create_admin.py
```

### Le token expire trop vite

Modifiez `.env` :
```env
ACCESS_TOKEN_EXPIRE_MINUTES=60  # 1 heure au lieu de 30 min
```

Puis redémarrez :
```bash
docker-compose restart backend
```

## Prochaines Étapes

Maintenant que l'authentification fonctionne, vous pouvez :

1. Créer des utilisateurs avec différents rôles
2. Tester les permissions
3. Passer à la Phase 2 Semaine 2 : Module Catalogue

## Logs

Pour voir les logs du backend :

```bash
docker-compose logs -f backend
```

Vous devriez voir les requêtes HTTP et les réponses.
