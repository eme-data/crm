FROM node:20-alpine

WORKDIR /app

# Copier package.json et package-lock.json
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier le reste du code
COPY . .

# Exposer le port Vite
EXPOSE 5173

# Commande de développement
CMD ["npm", "run", "dev", "--", "--host"]
