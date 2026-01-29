# Guide de Test - Module Catalogue

## Prérequis

1. L'application doit être démarrée :
   ```bash
   docker-compose up -d
   ```

2. Les migrations doivent être appliquées :
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

3. Un utilisateur admin doit exister :
   ```bash
   docker-compose exec backend python app/create_admin.py
   ```

## Étape 1 : Se connecter

1. Ouvrez http://localhost:8000/docs
2. POST `/api/auth/login` avec :
   ```json
   {
     "email": "admin@crm-btp.com",
     "password": "Admin123!"
   }
   ```
3. Copiez le `access_token`
4. Cliquez sur "Authorize" et collez le token

## Étape 2 : Tester l'API Materials

### Créer un matériau

**POST `/api/materials/`**

```json
{
  "code": "BOIS-001",
  "name_fr": "Planche Sapin 27x145x4000",
  "name_ro": "Scândură Brad 27x145x4000",
  "description": "Planche sapin brut",
  "unit": "u",
  "price_eur": 8.50,
  "price_lei": 41.23,
  "supplier": "Fournisseur Bois SA"
}
```

**Résultat attendu** : Status 201

```json
{
  "id": "uuid...",
  "code": "BOIS-001",
  "name_fr": "Planche Sapin 27x145x4000",
  "price_eur": 8.50,
  "is_active": true,
  ...
}
```

### Lister les matériaux

**GET `/api/materials/`**

Query params :
- `skip`: 0
- `limit`: 100
- `active_only`: true
- `search`: (optionnel)

**Résultat attendu** : Liste des matériaux

### Récupérer un matériau

**GET `/api/materials/{material_id}`**

Utilisez l'ID retourné lors de la création.

### Mettre à jour un matériau

**PUT `/api/materials/{material_id}`**

```json
{
  "price_eur": 9.00,
  "price_lei": 43.65
}
```

**Note** : La `price_date` sera automatiquement mise à jour.

### Supprimer un matériau (soft delete)

**DELETE `/api/materials/{material_id}`**

**Résultat attendu** : Status 204

Le matériau n'est pas supprimé mais marqué `is_active = false`.

## Étape 3 : Importer depuis Excel

### Préparer un fichier Excel de test

Créez un fichier `test_materials.xlsx` avec une feuille "Matériaux" :

| Code | Nom FR | Nom RO | Unité | Prix EUR | Prix LEI | Fournisseur |
|------|--------|--------|-------|----------|----------|-------------|
| BOIS-001 | Planche Sapin 27x145x4000 | Scândură Brad | u | 8.50 | 41.23 | Fournisseur 1 |
| BOIS-002 | Chevron 63x75x4000 | Căpriori 63x75 | u | 5.20 | 25.22 | Fournisseur 1 |
| ISO-001 | Laine de roche 100mm | Vată bazaltică | m2 | 4.80 | 23.28 | Fournisseur 2 |

### Détecter la structure du fichier

**POST `/api/import/excel/detect-structure`**

- Type: multipart/form-data
- file: `test_materials.xlsx`

**Résultat attendu** :

```json
{
  "filename": "test_materials.xlsx",
  "sheets": {
    "Matériaux": [
      "Code",
      "Nom FR",
      "Nom RO",
      "Unité",
      "Prix EUR",
      "Prix LEI",
      "Fournisseur"
    ]
  }
}
```

### Importer les matériaux

**POST `/api/import/excel/materials`**

Query params :
- `sheet_name`: "Matériaux"

Body :
- Type: multipart/form-data
- file: `test_materials.xlsx`

**Résultat attendu** :

```json
{
  "message": "Import réussi",
  "statistics": {
    "created": 3,
    "updated": 0,
    "errors": 0,
    "total": 3
  },
  "file": "test_materials.xlsx",
  "sheet": "Matériaux"
}
```

### Vérifier l'import

**GET `/api/materials/`**

Vous devriez voir les 3 matériaux importés.

## Étape 4 : Tester avec votre vraie matrice

### Importer votre matrice

Utilisez votre fichier :
`2 MATRICE DE PRETURI MARMANDE 28.11.2025 - Larox Franta complet fara OSB cabane.xlsx`

1. **Détecter la structure** :

```bash
# Via curl
curl -X POST http://localhost:8000/api/import/excel/detect-structure \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/matrice.xlsx"
```

Cela vous montrera tous les noms de feuilles et colonnes.

2. **Préparer les données** :

Si nécessaire, restructurez votre fichier Excel pour qu'il ait les colonnes attendues :
- `Code` ou `code`
- `Nom FR` ou `name_fr`
- `Nom RO` ou `name_ro` (optionnel)
- `Unité` ou `unit`
- `Prix EUR` ou `price_eur`
- `Prix LEI` ou `price_lei` (optionnel, sera calculé automatiquement)
- `Fournisseur` ou `supplier` (optionnel)

3. **Importer** :

```bash
curl -X POST "http://localhost:8000/api/import/excel/materials?sheet_name=NomDeLaFeuille" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/matrice.xlsx"
```

## Étape 5 : Vérifier dans la base de données

```bash
# Se connecter à PostgreSQL
docker-compose exec postgres psql -U crm_user -d crm_btp

# Compter les matériaux
SELECT COUNT(*) FROM materials;

# Voir les 10 premiers
SELECT code, name_fr, price_eur, unit FROM materials LIMIT 10;

# Rechercher un matériau spécifique
SELECT * FROM materials WHERE code LIKE 'BOIS%';

# Quitter
\q
```

## Calcul Automatique des Prix

### Principe

**Matériaux** :
- Prix stocké directement
- Conversion EUR ↔ LEI automatique

**Articles** (à venir Phase 2 Semaine 3) :
- Prix calculé = (Σ prix matériaux × quantité × (1 + waste) + main d'œuvre) × (1 + overhead) × (1 + margin)

**Compositions** (à venir) :
- Prix calculé = Σ (prix articles/matériaux × quantité) × (1 + overhead) × (1 + margin)

**Services** :
- Marge = Prix brut - Prix net

## Tests Avancés

### Test 1 : Import avec doublons

Importez deux fois le même fichier.

**Résultat attendu** :
- 1ère fois : `created: 3, updated: 0`
- 2ème fois : `created: 0, updated: 3`

### Test 2 : Recherche

**GET `/api/materials/?search=bois`**

Devrait retourner tous les matériaux contenant "bois" dans le code ou le nom.

### Test 3 : Pagination

**GET `/api/materials/?skip=0&limit=5`**  
**GET `/api/materials/?skip=5&limit=5`**

### Test 4 : Filtrer inactifs

1. Supprimer un matériau (devient inactif)
2. **GET `/api/materials/?active_only=false`** → Doit apparaître
3. **GET `/api/materials/?active_only=true`** → Ne doit PAS apparaître

## API Swagger

Toutes ces opérations peuvent être testées dans Swagger :
http://localhost:8000/docs

Vous y trouverez :
- **Authentication** : login, register, me, logout
- **Materials** : CRUD complet
- **Import** : detect-structure, import materials, import services

## Prochaines Étapes

**Phase 2 Semaine 3** (à venir) :
- API Articles avec composition de matériaux
- API Compositions
- API Services
- Calculs automatiques de prix
- Endpoints pour recalculer les prix

---

**✅ Si tous les tests passent, le Module Catalogue est fonctionnel !**
