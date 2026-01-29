"""
Utilitaires de sécurité
Hash de mots de passe et gestion des tokens JWT
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Configuration du hachage de mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifier un mot de passe contre son hash
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash du mot de passe
        
    Returns:
        bool: True si le mot de passe correspond
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hasher un mot de passe
    
    Args:
        password: Mot de passe en clair
        
    Returns:
        str: Hash du mot de passe
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Créer un token JWT d'accès
    
    Args:
        data: Données à encoder dans le token
        expires_delta: Durée de validité du token
        
    Returns:
        str: Token JWT encodé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Décoder un token JWT
    
    Args:
        token: Token JWT à décoder
        
    Returns:
        dict: Données décodées ou None si invalide
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
