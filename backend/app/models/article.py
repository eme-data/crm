"""
Modèle Article - Articles composés
Articles fabriqués à partir de matériaux et main d'œuvre
"""

from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Article(Base):
    """Modèle pour les articles (produits composés)"""
    
    __tablename__ = "articles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Unité
    unit = Column(String, nullable=False)
    
    # Prix calculés
    total_price = Column(Numeric(10, 2), nullable=False)
    material_cost = Column(Numeric(10, 2), nullable=False)
    labor_cost = Column(Numeric(10, 2), nullable=False)
    
    # Marges (en pourcentage décimal, ex: 0.30 pour 30%)
    margin = Column(Numeric(5, 4), nullable=False, default=0.30)
    overhead = Column(Numeric(5, 4), nullable=False, default=0.10)
    
    # Statut
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relations
    materials = relationship("ArticleMaterial", back_populates="article", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Article {self.code}: {self.name}>"


class ArticleMaterial(Base):
    """Table d'association Article-Material avec quantité"""
    
    __tablename__ = "article_materials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(UUID(as_uuid=True), ForeignKey("materials.id"), nullable=False)
    
    # Quantité nécessaire
    quantity = Column(Numeric(10, 4), nullable=False)
    
    # Pourcentage de perte/gaspillage (ex: 0.1 pour 10%)
    waste_percent = Column(Numeric(5, 4), default=0.0)
    
    # Relations
    article = relationship("Article", back_populates="materials")
    material = relationship("Material")
    
    def __repr__(self):
        return f"<ArticleMaterial article={self.article_id} material={self.material_id}>"


# Index pour améliorer les performances
Index('ix_articles_active', Article.is_active)
Index('ix_article_materials_article', ArticleMaterial.article_id)
