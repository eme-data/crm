"""
Schémas Pydantic pour l'authentification
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole


class UserBase(BaseModel):
    """Schéma de base pour les utilisateurs"""
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole = UserRole.COMMERCIAL


class UserCreate(UserBase):
    """Schéma pour la création d'utilisateur"""
    password: str


class UserUpdate(BaseModel):
    """Schéma pour la mise à jour d'utilisateur"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class User(UserBase):
    """Schéma pour le retour d'utilisateur"""
    id: str
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schéma pour le token JWT"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schéma pour les données du token"""
    email: Optional[str] = None
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    """Schéma pour la requête de login"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schéma pour la réponse de login"""
    access_token: str
    token_type: str
    user: User
