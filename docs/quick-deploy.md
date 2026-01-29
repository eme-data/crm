# Guide Rapide - Déploiement Production

## Option 1 : Installation Automatique (Recommandé)

```bash
# 1. Télécharger le script
wget https://votre-repo/scripts/install-crm-ubuntu.sh

# 2. Rendre exécutable
chmod +x install-crm-ubuntu.sh

# 3. Lancer l'installation
sudo bash install-crm-ubuntu.sh
```

Le script va vous demander :
- Nom de domaine (ex: crm.exemple.com)
- Email pour Let's Encrypt

Puis il installe automatiquement :
- Docker & Docker Compose
- Nginx
- SSL/HTTPS
- Fail2Ban
- Pare-feu (UFW)
- Backups automatiques

**Durée : 5-10 minutes**

---

## Option 2 : Installation Manuelle

Suivre le guide complet : [`docs/deployment-ubuntu.md`](deployment-ubuntu.md)

---

## Après l'installation

### 1. Cloner le projet

```bash
cd /var/www/crm-btp
git clone https://github.com/votre-username/crm.git .
```

### 2. Configurer .env

```bash
cp .env.example .env
nano .env
```

Modifier :
- `POSTGRES_PASSWORD` - Mot de passe PostgreSQL
- `SECRET_KEY` - Clé secrète JWT
- `CORS_ORIGINS` - Votre domaine

### 3. Démarrer l'application

```bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

### 4. Initialiser la base

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python app/create_admin.py
```

### 5. Accéder à l'app

Ouvrir : **https://crm.votre-domaine.com**

Login :
- Email : admin@crm-btp.com
- Password : Admin123!

---

## Commandes Utiles

```bash
# Voir les logs
docker compose -f docker-compose.prod.yml logs -f

# Redémarrer
docker compose -f docker-compose.prod.yml restart

# Backup manuel
/usr/local/bin/backup-crm.sh

# Monitoring
docker stats
htop
```

---

## Dépannage

**Problème SSL** :
```bash
sudo certbot renew
sudo systemctl restart nginx
```

**Problème Docker** :
```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

**Voir les erreurs** :
```bash
docker compose logs backend
sudo tail -f /var/log/nginx/error.log
```

---

## Checklist

- [ ] Nom de domaine DNS configuré
- [ ] Script d'installation exécuté
- [ ] Projet cloné dans /var/www/crm-btp
- [ ] Fichier .env configuré
- [ ] Docker containers démarrés
- [ ] Migrations appliquées
- [ ] Admin créé
- [ ] Application accessible en HTTPS
- [ ] Login fonctionnel

---

**Support** : Voir le guide complet dans [`docs/deployment-ubuntu.md`](deployment-ubuntu.md)
