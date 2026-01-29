"""
CRM BTP - Application FastAPI
Point d'entrée principal de l'API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.api import auth, materials, imports, articles, services


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    print("🚀 Démarrage de l'application CRM BTP...")
    print(f"📊 Base de données: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    
    # Créer les tables (pour le dev, en prod utiliser Alembic)
    # Base.metadata.create_all(bind=engine)
    
    yield
    
    # Shutdown
    print("👋 Arrêt de l'application CRM BTP...")


# Créer l'application FastAPI
app = FastAPI(
    title="CRM BTP API",
    description="API pour la gestion de devis et facturation dans le secteur immobilier/BTP",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes de base
@app.get("/")
async def root():
    """Route racine - Vérification du statut de l'API"""
    return {
        "message": "Bienvenue sur l'API CRM BTP",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Vérification de santé de l'application"""
    return {
        "status": "healthy",
        "database": "connected"  # TODO: vérifier vraiment la connexion DB
    }


# Enregistrer les routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(materials.router, prefix="/api/materials", tags=["Materials"])
app.include_router(articles.router, prefix="/api/articles", tags=["Articles"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(imports.router, prefix="/api/import", tags=["Import"])
# app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
# app.include_router(quotes.router, prefix="/api/quotes", tags=["Quotes"])
# app.include_router(invoices.router, prefix="/api/invoices", tags=["Invoices"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
