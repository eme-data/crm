# Guide de Déploiement Production - Ubuntu 24.04

**CRM BTP - Déploiement sur serveur Ubuntu 24.04**

---

## Table des Matières

1. [Prérequis](#prérequis)
2. [Installation du Serveur](#installation-du-serveur)
3. [Configuration Docker](#configuration-docker)
4. [Configuration de l'Application](#configuration-de-lapplication)
5. [Configuration Nginx](#configuration-nginx)
6. [SSL/HTTPS avec Let's Encrypt](#sslhttps-avec-lets-encrypt)
7. [Démarrage de l'Application](#démarrage-de-lapplication)
8. [Sécurité](#sécurité)
9. [Maintenance](#maintenance)
10. [Dépannage](#dépannage)

---

## Prérequis

### Serveur

- **OS** : Ubuntu 24.04 LTS (fraîchement installé)
- **RAM** : Minimum 2 GB (4 GB recommandé)
- **CPU** : Minimum 2 cores
- **Espace disque** : Minimum 20 GB
- **IP publique** : Avec nom de domaine pointé dessus

### Nom de domaine

Assurez-vous d'avoir un nom de domaine configuré :
- `crm.votre-domaine.com` → Pointe vers l'IP de votre serveur
- Enregistrement A configuré dans votre DNS

### Accès

- Accès SSH root ou sudo
- Ports ouverts : 22 (SSH), 80 (HTTP), 443 (HTTPS)

---

## Installation du Serveur

### 1. Mise à jour du système

```bash
# Se connecter en SSH
ssh root@votre-serveur-ip

# Mettre à jour les paquets
apt update && apt upgrade -y

# Installer les outils de base
apt install -y curl wget git vim ufw fail2ban
```

### 2. Créer un utilisateur non-root

```bash
# Créer l'utilisateur
adduser crm
usermod -aG sudo crm

# Copier les clés SSH (si vous utilisez des clés)
mkdir -p /home/crm/.ssh
cp ~/.ssh/authorized_keys /home/crm/.ssh/
chown -R crm:crm /home/crm/.ssh
chmod 700 /home/crm/.ssh
chmod 600 /home/crm/.ssh/authorized_keys

# Se connecter avec le nouvel utilisateur
su - crm
```

### 3. Configuration du pare-feu (UFW)

```bash
# Activer UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Autoriser SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activer le pare-feu
sudo ufw enable
sudo ufw status
```

---

## Configuration Docker

### 1. Installer Docker

```bash
# Supprimer les anciennes versions
sudo apt remove docker docker-engine docker.io containerd runc

# Installer les dépendances
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Ajouter la clé GPG Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Ajouter le dépôt Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Appliquer les changements (ou se reconnecter)
newgrp docker

# Vérifier l'installation
docker --version
docker compose version
```

### 2. Configurer Docker pour production

```bash
# Créer le fichier de configuration daemon
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true
}
EOF

# Redémarrer Docker
sudo systemctl restart docker
sudo systemctl enable docker
```

---

## Configuration de l'Application

### 1. Cloner le repository

```bash
# Créer le répertoire de l'application
sudo mkdir -p /var/www/crm-btp
sudo chown -R $USER:$USER /var/www/crm-btp
cd /var/www/crm-btp

# Cloner le projet
git clone https://github.com/votre-username/crm.git .
# OU copier les fichiers depuis votre machine locale avec scp
```

### 2. Configuration des variables d'environnement

```bash
# Créer le fichier .env
cat > .env <<EOF
# Database
POSTGRES_USER=crm_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_DB=crm_btp
DATABASE_URL=postgresql://crm_user:VOTRE_PASSWORD@postgres:5432/crm_btp

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=$(openssl rand -base64 64)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (votre domaine)
CORS_ORIGINS=https://crm.votre-domaine.com,http://localhost:5173

# Company
COMPANY_NAME=Votre Entreprise
COMPANY_CURRENCY=EUR
COMPANY_VAT_RATE=20.0
EUR_LEI_RATE=4.85
EOF

# Sécuriser le fichier
chmod 600 .env
```

> ⚠️ **Important** : Remplacez `VOTRE_PASSWORD` et `crm.votre-domaine.com` par vos valeurs.

### 3. Modifier docker-compose.yml pour production

```bash
# Créer docker-compose.prod.yml
cat > docker-compose.prod.yml <<'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16
    container_name: crm_postgres
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - crm_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: crm_redis
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - crm_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    container_name: crm_backend
    restart: always
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - crm_network
    expose:
      - "8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_URL: https://crm.votre-domaine.com
    container_name: crm_frontend
    restart: always
    depends_on:
      - backend
    networks:
      - crm_network
    expose:
      - "80"

networks:
  crm_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
EOF
```

### 4. Modifier Dockerfile frontend pour production

```bash
# Créer Dockerfile.prod dans frontend/
cat > frontend/Dockerfile.prod <<'EOF'
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF

# Créer nginx.conf pour SPA
cat > frontend/nginx.conf <<'EOF'
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF
```

---

## Configuration Nginx

### 1. Installer Nginx (reverse proxy)

```bash
sudo apt install -y nginx
```

### 2. Configuration Nginx pour le reverse proxy

```bash
# Créer la configuration
sudo tee /etc/nginx/sites-available/crm-btp <<'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name crm.votre-domaine.com;

    # Redirect HTTP to HTTPS (sera configuré après SSL)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 50M;
}
EOF

# Activer le site
sudo ln -s /etc/nginx/sites-available/crm-btp /etc/nginx/sites-enabled/

# Supprimer le site par défaut
sudo rm -f /etc/nginx/sites-enabled/default

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## SSL/HTTPS avec Let's Encrypt

### 1. Installer Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Obtenir le certificat SSL

```bash
# Obtenir le certificat
sudo certbot --nginx -d crm.votre-domaine.com

# Suivre les instructions :
# - Entrer votre email
# - Accepter les conditions
# - Choisir "2: Redirect" pour forcer HTTPS
```

### 3. Renouvellement automatique

```bash
# Tester le renouvellement
sudo certbot renew --dry-run

# Le cron job est automatiquement créé
sudo systemctl status certbot.timer
```

---

## Démarrage de l'Application

### 1. Build et démarrage

```bash
cd /var/www/crm-btp

# Build les images
docker compose -f docker-compose.prod.yml build

# Démarrer les services
docker compose -f docker-compose.prod.yml up -d

# Vérifier que tout tourne
docker compose -f docker-compose.prod.yml ps
```

### 2. Initialiser la base de données

```bash
# Appliquer les migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Créer l'utilisateur admin
docker compose -f docker-compose.prod.yml exec backend python app/create_admin.py
```

### 3. Vérifier l'application

```bash
# Tester le backend
curl http://localhost:8000/health

# Tester le frontend
curl http://localhost:5173

# Voir les logs
docker compose -f docker-compose.prod.yml logs -f
```

### 4. Accéder à l'application

Ouvrir dans un navigateur : **https://crm.votre-domaine.com**

---

## Sécurité

### 1. Fail2Ban pour SSH

```bash
# Installer Fail2Ban
sudo apt install -y fail2ban

# Configuration
sudo tee /etc/fail2ban/jail.local <<EOF
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

# Redémarrer
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

# Vérifier
sudo fail2ban-client status sshd
```

### 2. Sécuriser PostgreSQL

Les données sont déjà protégées car PostgreSQL n'est accessible que depuis le réseau Docker interne.

### 3. Backups automatiques

```bash
# Créer le script de backup
sudo tee /usr/local/bin/backup-crm.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/crm-btp"
DATE=$(date +%Y%m%d_%H%M%S)

# Créer le répertoire de backup
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec crm_postgres pg_dump -U crm_user crm_btp | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup fichiers uploadés (si applicable)
# tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/crm-btp/uploads

# Garder seulement les 7 derniers jours
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

# Rendre exécutable
sudo chmod +x /usr/local/bin/backup-crm.sh

# Ajouter au crontab (tous les jours à 2h du matin)
sudo crontab -e
# Ajouter cette ligne :
# 0 2 * * * /usr/local/bin/backup-crm.sh >> /var/log/crm-backup.log 2>&1
```

### 4. Monitoring

```bash
# Installer htop pour monitoring
sudo apt install -y htop

# Voir l'utilisation système
htop

# Voir l'utilisation Docker
docker stats
```

---

## Maintenance

### Mise à jour de l'application

```bash
cd /var/www/crm-btp

# Arrêter les services
docker compose -f docker-compose.prod.yml down

# Pull les dernières modifications
git pull origin main

# Rebuild les images
docker compose -f docker-compose.prod.yml build

# Redémarrer
docker compose -f docker-compose.prod.yml up -d

# Appliquer les nouvelles migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Voir les logs

```bash
# Tous les logs
docker compose -f docker-compose.prod.yml logs -f

# Logs d'un service spécifique
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f postgres

# Logs Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Redémarrer les services

```bash
# Redémarrer tout
docker compose -f docker-compose.prod.yml restart

# Redémarrer un service
docker compose -f docker-compose.prod.yml restart backend
```

---

## Dépannage

### Problème 1 : Application inaccessible

```bash
# Vérifier que Nginx tourne
sudo systemctl status nginx
sudo nginx -t

# Vérifier les containers Docker
docker compose -f docker-compose.prod.yml ps

# Vérifier les logs
docker compose -f docker-compose.prod.yml logs
```

### Problème 2 : Erreurs de base de données

```bash
# Se connecter à PostgreSQL
docker exec -it crm_postgres psql -U crm_user -d crm_btp

# Voir les tables
\dt

# Quitter
\q

# Réappliquer les migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Problème 3 : Certificat SSL expiré

```bash
# Renouveler manuellement
sudo certbot renew

# Redémarrer Nginx
sudo systemctl restart nginx
```

### Problème 4 : Manque d'espace disque

```bash
# Vérifier l'espace
df -h

# Nettoyer les images Docker inutilisées
docker system prune -a

# Nettoyer les logs
sudo journalctl --vacuum-time=7d
```

---

## Checklist de Déploiement

Avant de mettre en production, vérifier :

- [ ] Nom de domaine configuré et DNS propagé
- [ ] Serveur Ubuntu 24.04 à jour
- [ ] Pare-feu (UFW) configuré
- [ ] Docker et Docker Compose installés
- [ ] Variables d'environnement (.env) configurées avec des secrets forts
- [ ] Base de données initialisée avec migrations
- [ ] Utilisateur admin créé
- [ ] Nginx configuré comme reverse proxy
- [ ] SSL/HTTPS activé avec Let's Encrypt
- [ ] Backups automatiques configurés
- [ ] Fail2Ban activé pour SSH
- [ ] Application accessible via HTTPS
- [ ] Login fonctionnel
- [ ] Import Excel testé
- [ ] Logs fonctionnels

---

## Contacts et Support

**En cas de problème** :
- Vérifier les logs : `docker compose logs -f`
- Vérifier Nginx : `sudo systemctl status nginx`
- Vérifier le pare-feu : `sudo ufw status`

**Métriques à surveiller** :
- Utilisation CPU/RAM : `htop`
- Espace disque : `df -h`
- Logs erreurs : `tail -f /var/log/nginx/error.log`

---

**🎉 Votre CRM BTP est maintenant en production !**
