"""
Modèle Material - Matériaux
Gestion des matériaux de base (bois, quincaillerie, isolants, etc.)
"""

from sqlalchemy import Column, String, Numeric, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class Material(Base):
    """Modèle pour les matériaux"""
    
    __tablename__ = "materials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, index=True, nullable=False)
    name_fr = Column(String, nullable=False)
    name_ro = Column(String, nullable=True)  # Nom en roumain (optionnel)
    description = Column(String, nullable=True)
    
    # Unité de mesure
    unit = Column(String, nullable=False)  # m2, m3, kg, l, u, etc.
    
    # Prix
    price_eur = Column(Numeric(10, 2), nullable=False)
    price_lei = Column(Numeric(10, 2), nullable=True)
    
    # Métadonnées prix
    price_date = Column(String, default=lambda: datetime.utcnow().isoformat())
    supplier = Column(String, nullable=True)
    
    # Statut
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    def __repr__(self):
        return f"<Material {self.code}: {self.name_fr}>"


# Index supplémentaire pour les requêtes fréquentes
Index('ix_materials_active', Material.is_active)
