"""
Configuration de l'application
Gestion des variables d'environnement avec Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Application
    APP_NAME: str = "CRM BTP"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://crm_user:changeme@postgres:5432/crm_btp"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-characters"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost",
    ]
    
    # Company Settings
    COMPANY_NAME: str = "Larox Franta"
    DEFAULT_CURRENCY: str = "EUR"
    EUR_LEI_RATE: float = 4.85
    DEFAULT_MARGIN: float = 0.30
    DEFAULT_OVERHEAD: float = 0.10
    DEFAULT_VAT_RATE: float = 0.19
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instance globale des settings
settings = Settings()
