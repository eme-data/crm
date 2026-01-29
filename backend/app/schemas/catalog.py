"""
Schémas Pydantic pour le catalogue
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal


# ========== MATERIALS ==========

class MaterialBase(BaseModel):
    """Schéma de base pour les matériaux"""
    code: str = Field(..., min_length=1, max_length=50)
    name_fr: str = Field(..., min_length=1)
    name_ro: Optional[str] = None
    description: Optional[str] = None
    unit: str = Field(..., min_length=1, max_length=20)
    price_eur: Decimal = Field(..., ge=0, decimal_places=2)
    price_lei: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    supplier: Optional[str] = None


class MaterialCreate(MaterialBase):
    """Schéma pour la création d'un matériau"""
    pass


class MaterialUpdate(BaseModel):
    """Schéma pour la mise à jour d'un matériau"""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name_fr: Optional[str] = Field(None, min_length=1)
    name_ro: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    price_eur: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    price_lei: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    supplier: Optional[str] = None
    is_active: Optional[bool] = None


class Material(MaterialBase):
    """Schéma pour le retour d'un matériau"""
    id: str
    price_date: str
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


# ========== ARTICLES ==========

class ArticleMaterialBase(BaseModel):
    """Schéma pour l'association article-matériau"""
    material_id: str
    quantity: Decimal = Field(..., gt=0)
    waste_percent: Decimal = Field(default=0.0, ge=0, le=1)


class ArticleMaterialCreate(ArticleMaterialBase):
    pass


class ArticleMaterial(ArticleMaterialBase):
    """Schéma pour le retour d'une association article-matériau"""
    id: str
    article_id: str
    material: Optional[Material] = None
    
    class Config:
        from_attributes = True


class ArticleBase(BaseModel):
    """Schéma de base pour les articles"""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    unit: str = Field(..., min_length=1, max_length=20)
    margin: Decimal = Field(default=0.30, ge=0, le=1)
    overhead: Decimal = Field(default=0.10, ge=0, le=1)


class ArticleCreate(ArticleBase):
    """Schéma pour la création d'un article"""
    labor_cost: Decimal = Field(default=0.0, ge=0, decimal_places=2)
    materials: List[ArticleMaterialCreate] = []


class ArticleUpdate(BaseModel):
    """Schéma pour la mise à jour d'un article"""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    labor_cost: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    margin: Optional[Decimal] = Field(None, ge=0, le=1)
    overhead: Optional[Decimal] = Field(None, ge=0, le=1)
    is_active: Optional[bool] = None


class Article(ArticleBase):
    """Schéma pour le retour d'un article"""
    id: str
    total_price: Decimal
    material_cost: Decimal
    labor_cost: Decimal
    is_active: bool
    created_at: str
    updated_at: str
    materials: List[ArticleMaterial] = []
    
    class Config:
        from_attributes = True


# ========== COMPOSITIONS ==========

class CompositionItemBase(BaseModel):
    """Schéma pour les items de composition"""
    item_type: str = Field(..., pattern='^(material|article)$')
    item_id: str
    quantity: Decimal = Field(..., gt=0)


class CompositionItemCreate(CompositionItemBase):
    pass


class CompositionItem(CompositionItemBase):
    """Schéma pour le retour d'un item de composition"""
    id: str
    composition_id: str
    
    class Config:
        from_attributes = True


class CompositionBase(BaseModel):
    """Schéma de base pour les compositions"""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    unit: str = Field(..., min_length=1, max_length=20)
    margin: Decimal = Field(default=0.30, ge=0, le=1)
    overhead: Decimal = Field(default=0.10, ge=0, le=1)


class CompositionCreate(CompositionBase):
    """Schéma pour la création d'une composition"""
    items: List[CompositionItemCreate] = []


class CompositionUpdate(BaseModel):
    """Schéma pour la mise à jour d'une composition"""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    margin: Optional[Decimal] = Field(None, ge=0, le=1)
    overhead: Optional[Decimal] = Field(None, ge=0, le=1)
    is_active: Optional[bool] = None


class Composition(CompositionBase):
    """Schéma pour le retour d'une composition"""
    id: str
    total_price: Decimal
    is_active: bool
    created_at: str
    updated_at: str
    items: List[CompositionItem] = []
    
    class Config:
        from_attributes = True


# ========== SERVICES ==========

class ServiceBase(BaseModel):
    """Schéma de base pour les services"""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    unit: str = Field(..., min_length=1, max_length=20)
    price_net: Decimal = Field(..., ge=0, decimal_places=2)
    price_gross: Decimal = Field(..., ge=0, decimal_places=2)


class ServiceCreate(ServiceBase):
    """Schéma pour la création d'un service"""
    pass


class ServiceUpdate(BaseModel):
    """Schéma pour la mise à jour d'un service"""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    price_net: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    price_gross: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    is_active: Optional[bool] = None


class Service(ServiceBase):
    """Schéma pour le retour d'un service"""
    id: str
    margin: Decimal
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
