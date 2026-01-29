"""
Script pour créer un utilisateur administrateur initial
"""

import sys
import os

# Ajouter le path du backend pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import get_password_hash
import uuid


def create_admin_user():
    """Créer un utilisateur administrateur par défaut"""
    
    db = SessionLocal()
    
    try:
        # Vérifier si un admin existe déjà
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if existing_admin:
            print(f"✓ Un administrateur existe déjà: {existing_admin.email}")
            return
        
        # Créer l'admin
        admin_email = "admin@crm-btp.com"
        admin_password = "Admin123!"  # À changer après la première connexion
        
        admin_user = User(
            id=uuid.uuid4(),
            email=admin_email,
            password_hash=get_password_hash(admin_password),
            first_name="Admin",
            last_name="CRM BTP",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("=" * 60)
        print("✅ Utilisateur administrateur créé avec succès!")
        print("=" * 60)
        print(f"Email:        {admin_email}")
        print(f"Mot de passe: {admin_password}")
        print("=" * 60)
        print("⚠️  IMPORTANT: Changez ce mot de passe après votre première connexion!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
