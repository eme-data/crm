"""
Modèle Composition - Compositions complexes
Assemblages d'articles et/ou matériaux
"""

from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class CompositionItemType(str, enum.Enum):
    """Types d'items dans une composition"""
    MATERIAL = "material"
    ARTICLE = "article"


class Composition(Base):
    """Modèle pour les compositions (assemblages complexes)"""
    
    __tablename__ = "compositions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Unité
    unit = Column(String, nullable=False)
    
    # Prix calculés
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Marges
    margin = Column(Numeric(5, 4), nullable=False, default=0.30)
    overhead = Column(Numeric(5, 4), nullable=False, default=0.10)
    
    # Statut
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relations
    items = relationship("CompositionItem", back_populates="composition", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Composition {self.code}: {self.name}>"


class CompositionItem(Base):
    """Items dans une composition (peut être un article ou un matériau)"""
    
    __tablename__ = "composition_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    composition_id = Column(UUID(as_uuid=True), ForeignKey("compositions.id", ondelete="CASCADE"), nullable=False)
    
    # Type d'item (material ou article)
    item_type = Column(SQLEnum(CompositionItemType), nullable=False)
    
    # ID de l'item (soit material_id soit article_id)
    item_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Quantité
    quantity = Column(Numeric(10, 4), nullable=False)
    
    # Relations
    composition = relationship("Composition", back_populates="items")
    
    def __repr__(self):
        return f"<CompositionItem {self.item_type}={self.item_id}>"


# Index
Index('ix_compositions_active', Composition.is_active)
Index('ix_composition_items_composition', CompositionItem.composition_id)
