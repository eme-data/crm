"""
Modèle Client - Gestion des clients et prospects
"""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.database import Base


class ClientType(str, enum.Enum):
    """Types de clients"""
    PROSPECT = "prospect"
    CLIENT = "client"
    PARTNER = "partner"


class Client(Base):
    """Modèle pour les clients et prospects"""
    
    __tablename__ = "clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Type
    client_type = Column(SQLEnum(ClientType), default=ClientType.PROSPECT, nullable=False)
    
    # Informations entreprise
    company_name = Column(String, nullable=False, index=True)
    siret = Column(String, nullable=True)
    vat_number = Column(String, nullable=True)
    
    # Contact principal
    contact_first_name = Column(String, nullable=True)
    contact_last_name = Column(String, nullable=True)
    contact_email = Column(String, nullable=True, index=True)
    contact_phone = Column(String, nullable=True)
    
    # Adresse
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, default="France", nullable=False)
    
    # Notes
    notes = Column(String, nullable=True)
    
    # Statut
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    def __repr__(self):
        return f"<Client {self.company_name} ({self.client_type})>"


# Index
Index('ix_clients_active', Client.is_active)
Index('ix_clients_type', Client.client_type)
