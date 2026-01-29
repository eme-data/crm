"""
Service d'authentification
Gestion de la logique métier de l'authentification
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, LoginRequest
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.config import settings


class AuthService:
    """Service pour gérer l'authentification"""
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authentifier un utilisateur
        
        Args:
            db: Session de base de données
            email: Email de l'utilisateur
            password: Mot de passe en clair
            
        Returns:
            User ou None si authentification échoue
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Créer un nouvel utilisateur
        
        Args:
            db: Session de base de données
            user_data: Données de l'utilisateur
            
        Returns:
            User créé
            
        Raises:
            HTTPException si l'email existe déjà
        """
        # Vérifier si l'email existe déjà
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec cet email existe déjà"
            )
        
        # Créer l'utilisateur
        user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> dict:
        """
        Connecter un utilisateur
        
        Args:
            db: Session de base de données
            login_data: Données de connexion
            
        Returns:
            Dict avec access_token et user
            
        Raises:
            HTTPException si authentification échoue
        """
        user = AuthService.authenticate_user(
            db, 
            login_data.email, 
            login_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Créer le token JWT
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
