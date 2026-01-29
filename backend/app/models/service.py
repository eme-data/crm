"""
Modèle Service - Services et prestations
Services forfaitaires (transport, études, etc.)
"""

from sqlalchemy import Column, String, Numeric, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class Service(Base):
    """Modèle pour les services et prestations"""
    
    __tablename__ = "services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Unité (ft=forfait, j=jour, h=heure, ens=ensemble, etc.)
    unit = Column(String, nullable=False)
    
    # Prix
    price_net = Column(Numeric(10, 2), nullable=False)  # Prix net (coût)
    price_gross = Column(Numeric(10, 2), nullable=False)  # Prix brut (vente)
    
    # Marge calculée (gross - net)
    margin = Column(Numeric(10, 2), nullable=False, default=0.0)
    
    # Statut
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    def __repr__(self):
        return f"<Service {self.code}: {self.name}>"


# Index
Index('ix_services_active', Service.is_active)
