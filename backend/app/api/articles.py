"""
Routes API pour les articles
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.database import get_db
from app.schemas.catalog import Article, ArticleCreate, ArticleUpdate
from app.models.article import Article as ArticleModel, ArticleMaterial
from app.models.material import Material
from app.services.price_calculator import PriceCalculator
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


@router.get("/", response_model=List[Article])
async def list_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister les articles"""
    query = db.query(ArticleModel)
    
    if active_only:
        query = query.filter(ArticleModel.is_active == True)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (ArticleModel.code.ilike(search_filter)) |
            (ArticleModel.name.ilike(search_filter))
        )
    
    articles = query.offset(skip).limit(limit).all()
    return articles


@router.get("/{article_id}", response_model=Article)
async def get_article(
    article_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un article par ID"""
    article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article non trouvé"
        )
    
    return article


@router.post("/", response_model=Article, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Créer un nouvel article
    
    Les prix sont calculés automatiquement :
    - material_cost = Σ(prix matériau × quantité × (1 + waste))
    - total_price = (material_cost + labor_cost) × (1 + overhead) × (1 + margin)
    """
    # Vérifier si le code existe déjà
    existing = db.query(ArticleModel).filter(ArticleModel.code == article_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un article avec le code '{article_data.code}' existe déjà"
        )
    
    # Créer l'article
    article = ArticleModel(
        id=uuid.uuid4(),
        code=article_data.code,
        name=article_data.name,
        description=article_data.description,
        unit=article_data.unit,
        labor_cost=article_data.labor_cost,
        margin=article_data.margin,
        overhead=article_data.overhead,
        material_cost=0,
        total_price=0
    )
    
    db.add(article)
    db.flush()  # Pour obtenir l'ID
    
    # Ajouter les matériaux
    for material_data in article_data.materials:
        # Vérifier que le matériau existe
        material = db.query(Material).filter(Material.id == material_data.material_id).first()
        if not material:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Matériau {material_data.material_id} non trouvé"
            )
        
        article_material = ArticleMaterial(
            id=uuid.uuid4(),
            article_id=article.id,
            material_id=material_data.material_id,
            quantity=material_data.quantity,
            waste_percent=material_data.waste_percent
        )
        db.add(article_material)
    
    db.flush()
    
    # Calculer les prix
    prices = PriceCalculator.calculate_article_price(article, db)
    article.material_cost = prices['material_cost']
    article.total_price = prices['total_price']
    
    db.commit()
    db.refresh(article)
    
    return article


@router.put("/{article_id}", response_model=Article)
async def update_article(
    article_id: str,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un article et recalculer les prix"""
    article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article non trouvé"
        )
    
    # Vérifier le code unique si modifié
    if article_data.code and article_data.code != article.code:
        existing = db.query(ArticleModel).filter(ArticleModel.code == article_data.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Un article avec le code '{article_data.code}' existe déjà"
            )
    
    # Mettre à jour les champs
    update_data = article_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(article, field, value)
    
    article.updated_at = datetime.utcnow().isoformat()
    
    # Recalculer les prix
    prices = PriceCalculator.calculate_article_price(article, db)
    article.material_cost = prices['material_cost']
    article.total_price = prices['total_price']
    
    db.commit()
    db.refresh(article)
    
    return article


@router.post("/{article_id}/recalculate", response_model=Article)
async def recalculate_article_price(
    article_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recalculer les prix d'un article
    
    Utile quand les prix des matériaux ont changé
    """
    article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article non trouvé"
        )
    
    # Recalculer
    prices = PriceCalculator.calculate_article_price(article, db)
    article.material_cost = prices['material_cost']
    article.total_price = prices['total_price']
    article.updated_at = datetime.utcnow().isoformat()
    
    db.commit()
    db.refresh(article)
    
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un article (soft delete)"""
    article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article non trouvé"
        )
    
    # Soft delete
    article.is_active = False
    article.updated_at = datetime.utcnow().isoformat()
    
    db.commit()
    
    return None
