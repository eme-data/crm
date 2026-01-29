#!/bin/bash

###############################################################################
# Script d'installation automatique CRM BTP sur Ubuntu 24.04
# Usage: sudo bash install-crm-ubuntu.sh
###############################################################################

set -e  # Exit on error

echo "========================================="
echo "Installation CRM BTP - Ubuntu 24.04"
echo "========================================="
echo ""

# Vérifier qu'on est sur Ubuntu 24.04
if [ ! -f /etc/lsb-release ]; then
    echo "❌ Ce script est conçu pour Ubuntu 24.04"
    exit 1
fi

source /etc/lsb-release
if [ "$DISTRIB_ID" != "Ubuntu" ] || [ "$DISTRIB_RELEASE" != "24.04" ]; then
    echo "❌ Ce script nécessite Ubuntu 24.04"
    echo "Votre version: $DISTRIB_ID $DISTRIB_RELEASE"
    exit 1
fi

# Vérifier root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Ce script doit être exécuté en tant que root"
    echo "Utilisez: sudo bash install-crm-ubuntu.sh"
    exit 1
fi

echo "✅ Système: Ubuntu 24.04"
echo ""

# Demander le nom de domaine
read -p "Nom de domaine (ex: crm.exemple.com): " DOMAIN_NAME
if [ -z "$DOMAIN_NAME" ]; then
    echo "❌ Le nom de domaine est obligatoire"
    exit 1
fi

# Demander l'email pour SSL
read -p "Email pour Let's Encrypt: " SSL_EMAIL
if [ -z "$SSL_EMAIL" ]; then
    echo "❌ L'email est obligatoire pour SSL"
    exit 1
fi

echo ""
echo "Configuration:"
echo "- Domaine: $DOMAIN_NAME"
echo "- Email SSL: $SSL_EMAIL"
echo ""
read -p "Continuer l'installation? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Installation annulée"
    exit 0
fi

echo ""
echo "========================================="
echo "1. Mise à jour du système"
echo "========================================="
apt update && apt upgrade -y
apt install -y curl wget git vim ufw fail2ban

echo ""
echo "========================================="
echo "2. Configuration du pare-feu (UFW)"
echo "========================================="
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw status

echo ""
echo "========================================="
echo "3. Installation de Docker"
echo "========================================="

# Supprimer anciennes versions
apt remove -y docker docker-engine docker.io containerd runc || true

# Installer les dépendances
apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Ajouter la clé GPG Docker
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Ajouter le dépôt
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Configuration Docker
cat > /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true
}
EOF

systemctl restart docker
systemctl enable docker

echo "✅ Docker installé: $(docker --version)"

echo ""
echo "========================================="
echo "4. Installation de Nginx"
echo "========================================="
apt install -y nginx
systemctl enable nginx

echo ""
echo "========================================="
echo "5. Installation de Certbot (Let's Encrypt)"
echo "========================================="
apt install -y certbot python3-certbot-nginx

echo ""
echo "========================================="
echo "6. Configuration de Fail2Ban"
echo "========================================="
cat > /etc/fail2ban/jail.local <<EOF
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

systemctl restart fail2ban
systemctl enable fail2ban

echo ""
echo "========================================="
echo "7. Création des répertoires"
echo "========================================="
mkdir -p /var/www/crm-btp
mkdir -p /var/backups/crm-btp

echo ""
echo "========================================="
echo "8. Configuration Nginx"
echo "========================================="
cat > /etc/nginx/sites-available/crm-btp <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN_NAME;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    client_max_body_size 50M;
}
EOF

ln -sf /etc/nginx/sites-available/crm-btp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx

echo ""
echo "========================================="
echo "9. Configuration SSL avec Let's Encrypt"
echo "========================================="
certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email $SSL_EMAIL --redirect

echo ""
echo "========================================="
echo "10. Script de backup automatique"
echo "========================================="
cat > /usr/local/bin/backup-crm.sh <<'EOFBACKUP'
#!/bin/bash
BACKUP_DIR="/var/backups/crm-btp"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
docker exec crm_postgres pg_dump -U crm_user crm_btp | gzip > $BACKUP_DIR/db_$DATE.sql.gz
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
echo "Backup completed: $DATE"
EOFBACKUP

chmod +x /usr/local/bin/backup-crm.sh

# Ajouter au crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-crm.sh >> /var/log/crm-backup.log 2>&1") | crontab -

echo ""
echo "========================================="
echo "Installation terminée ✅"
echo "========================================="
echo ""
echo "Prochaines étapes:"
echo ""
echo "1. Cloner votre projet dans /var/www/crm-btp"
echo "   cd /var/www/crm-btp"
echo "   git clone https://github.com/votre-repo/crm.git ."
echo ""
echo "2. Créer le fichier .env avec vos secrets"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "3. Démarrer l'application"
echo "   docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "4. Initialiser la base de données"
echo "   docker compose exec backend alembic upgrade head"
echo "   docker compose exec backend python app/create_admin.py"
echo ""
echo "5. Accéder à l'application"
echo "   https://$DOMAIN_NAME"
echo ""
echo "Informations système:"
echo "- Docker: $(docker --version)"
echo "- Nginx: $(nginx -v 2>&1)"
echo "- SSL: Let's Encrypt configuré"
echo "- Backups: Quotidiens à 2h du matin"
echo "- Pare-feu: UFW activé (ports 22, 80, 443)"
echo "- Fail2Ban: Activé pour SSH"
echo ""
echo "Logs utiles:"
echo "- Application: docker compose logs -f"
echo "- Nginx: tail -f /var/log/nginx/error.log"
echo "- Backups: tail -f /var/log/crm-backup.log"
echo ""
echo "========================================="
echo "Installation réussie ! 🎉"
echo "========================================="
