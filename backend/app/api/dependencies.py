"""
Dépendances pour l'authentification
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token
from app.config import settings


# OAuth2 scheme pour récupérer le token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Récupérer l'utilisateur actuel à partir du token JWT
    
    Args:
        token: Token JWT
        db: Session de base de données
        
    Returns:
        User authentifié
        
    Raises:
        HTTPException si token invalide
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
        
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    # Récupérer l'utilisateur depuis la DB
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisateur inactif"
        )
    
    return user


async def get_current_active_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Vérifier que l'utilisateur actuel est un admin
    
    Args:
        current_user: Utilisateur actuel
        
    Returns:
        User si admin
        
    Raises:
        HTTPException si pas admin
    """
    from app.models.user import UserRole
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    
    return current_user
