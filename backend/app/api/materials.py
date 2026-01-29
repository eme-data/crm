"""
Routes API pour les matériaux
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.database import get_db
from app.schemas.catalog import Material, MaterialCreate, MaterialUpdate
from app.models.material import Material as MaterialModel
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


@router.get("/", response_model=List[Material])
async def list_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lister les matériaux
    
    - **skip**: Nombre d'éléments à sauter (pagination)
    - **limit**: Nombre maximum d'éléments à retourner
    - **active_only**: Ne retourner que les matériaux actifs
    - **search**: Rechercher dans le code ou le nom
    """
    query = db.query(MaterialModel)
    
    if active_only:
        query = query.filter(MaterialModel.is_active == True)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (MaterialModel.code.ilike(search_filter)) |
            (MaterialModel.name_fr.ilike(search_filter)) |
            (MaterialModel.name_ro.ilike(search_filter))
        )
    
    materials = query.offset(skip).limit(limit).all()
    return materials


@router.get("/{material_id}", response_model=Material)
async def get_material(
    material_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un matériau par ID"""
    material = db.query(MaterialModel).filter(MaterialModel.id == material_id).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matériau non trouvé"
        )
    
    return material


@router.post("/", response_model=Material, status_code=status.HTTP_201_CREATED)
async def create_material(
    material_data: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Créer un nouveau matériau
    
    Requiert: Utilisateur authentifié
    """
    # Vérifier si le code existe déjà
    existing = db.query(MaterialModel).filter(MaterialModel.code == material_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un matériau avec le code '{material_data.code}' existe déjà"
        )
    
    # Créer le matériau
    material = MaterialModel(
        id=uuid.uuid4(),
        **material_data.model_dump()
    )
    
    db.add(material)
    db.commit()
    db.refresh(material)
    
    return material


@router.put("/{material_id}", response_model=Material)
async def update_material(
    material_id: str,
    material_data: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mettre à jour un matériau
    
    Requiert: Utilisateur authentifié
    """
    material = db.query(MaterialModel).filter(MaterialModel.id == material_id).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matériau non trouvé"
        )
    
    # Vérifier le code unique si modifié
    if material_data.code and material_data.code != material.code:
        existing = db.query(MaterialModel).filter(MaterialModel.code == material_data.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Un matériau avec le code '{material_data.code}' existe déjà"
            )
    
    # Mettre à jour les champs
    update_data = material_data.model_dump(exclude_unset=True)
    
    # Si le prix est modifié, mettre à jour la date
    if 'price_eur' in update_data or 'price_lei' in update_data:
        update_data['price_date'] = datetime.utcnow().isoformat()
    
    for field, value in update_data.items():
        setattr(material, field, value)
    
    material.updated_at = datetime.utcnow().isoformat()
    
    db.commit()
    db.refresh(material)
    
    return material


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprimer un matériau (soft delete)
    
    Requiert: Utilisateur authentifié
    """
    material = db.query(MaterialModel).filter(MaterialModel.id == material_id).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matériau non trouvé"
        )
    
    # Soft delete
    material.is_active = False
    material.updated_at = datetime.utcnow().isoformat()
    
    db.commit()
    
    return None
