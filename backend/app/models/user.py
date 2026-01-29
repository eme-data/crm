"""
Modèle User - Gestion des utilisateurs
"""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """Rôles disponibles pour les utilisateurs"""
    ADMIN = "admin"
    COMMERCIAL = "commercial"
    GESTIONNAIRE = "gestionnaire"
    COMPTABLE = "comptable"


class User(Base):
    """Modèle pour les utilisateurs du système"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.COMMERCIAL, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
