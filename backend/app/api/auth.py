"""
Routes d'authentification
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import LoginRequest, LoginResponse, UserCreate, User as UserSchema
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Créer un nouveau compte utilisateur
    
    - **email**: Email unique de l'utilisateur
    - **password**: Mot de passe (sera hashé)
    - **first_name**: Prénom
    - **last_name**: Nom
    - **role**: Rôle de l'utilisateur (admin, commercial, gestionnaire, comptable)
    """
    user = AuthService.create_user(db, user_data)
    return user


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Se connecter avec email et mot de passe
    
    Retourne un token JWT à utiliser dans les requêtes suivantes.
    
    - **email**: Email de l'utilisateur
    - **password**: Mot de passe
    """
    result = AuthService.login(db, login_data)
    return result


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Récupérer les informations de l'utilisateur connecté
    
    Requiert un token JWT valide dans le header Authorization.
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Se déconnecter
    
    Note: Avec JWT, la déconnexion côté serveur est optionnelle.
    Le client doit supprimer le token de son stockage local.
    """
    return {
        "message": "Déconnexion réussie",
        "detail": "Le token restera valide jusqu'à son expiration. Supprimez-le côté client."
    }
