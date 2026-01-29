"""
Routes API pour les services
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.database import get_db
from app.schemas.catalog import Service, ServiceCreate, ServiceUpdate
from app.models.service import Service as ServiceModel
from app.services.price_calculator import PriceCalculator
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


@router.get("/", response_model=List[Service])
async def list_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister les services"""
    query = db.query(ServiceModel)
    
    if active_only:
        query = query.filter(ServiceModel.is_active == True)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (ServiceModel.code.ilike(search_filter)) |
            (ServiceModel.name.ilike(search_filter))
        )
    
    services = query.offset(skip).limit(limit).all()
    return services


@router.get("/{service_id}", response_model=Service)
async def get_service(
    service_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un service par ID"""
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service non trouvé"
        )
    
    return service


@router.post("/", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Créer un nouveau service
    
    La marge est calculée automatiquement : margin = price_gross - price_net
    """
    # Vérifier si le code existe déjà
    existing = db.query(ServiceModel).filter(ServiceModel.code == service_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un service avec le code '{service_data.code}' existe déjà"
        )
    
    # Calculer la marge
    margin = PriceCalculator.calculate_service_margin(
        service_data.price_net,
        service_data.price_gross
    )
    
    # Créer le service
    service = ServiceModel(
        id=uuid.uuid4(),
        **service_data.model_dump(),
        margin=margin
    )
    
    db.add(service)
    db.commit()
    db.refresh(service)
    
    return service


@router.put("/{service_id}", response_model=Service)
async def update_service(
    service_id: str,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un service"""
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service non trouvé"
        )
    
    # Vérifier le code unique si modifié
    if service_data.code and service_data.code != service.code:
        existing = db.query(ServiceModel).filter(ServiceModel.code == service_data.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Un service avec le code '{service_data.code}' existe déjà"
            )
    
    # Mettre à jour les champs
    update_data = service_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(service, field, value)
    
    # Recalculer la marge si les prix ont changé
    if 'price_net' in update_data or 'price_gross' in update_data:
        service.margin = PriceCalculator.calculate_service_margin(
            service.price_net,
            service.price_gross
        )
    
    service.updated_at = datetime.utcnow().isoformat()
    
    db.commit()
    db.refresh(service)
    
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un service (soft delete)"""
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service non trouvé"
        )
    
    # Soft delete
    service.is_active = False
    service.updated_at = datetime.utcnow().isoformat()
    
    db.commit()
    
    return None
