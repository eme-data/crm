"""
Configuration de la base de données
SQLAlchemy setup et session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings

# Créer le moteur de base de données
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Créer la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency pour obtenir une session de base de données
    
    Yields:
        Session: Session de base de données SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
