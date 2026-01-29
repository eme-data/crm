"""
Service d'import Excel
Importer la matrice de prix depuis un fichier Excel
"""

import pandas as pd
from typing import List, Dict, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.models.material import Material
from app.models.article import Article, ArticleMaterial
from app.models.service import Service
from app.services.price_calculator import PriceCalculator


class ExcelImportService:
    """Service pour importer des données depuis Excel"""
    
    @staticmethod
    def import_materials_from_excel(
        file_path: str,
        db: Session,
        sheet_name: str = "Matériaux"
    ) -> Dict[str, int]:
        """
        Importer des matériaux depuis un fichier Excel
        
        Format attendu :
        - Code | Nom FR | Nom RO | Unité | Prix EUR | Prix LEI | Fournisseur
        
        Args:
            file_path: Chemin du fichier Excel
            db: Session de base de données
            sheet_name: Nom de la feuille à lire
            
        Returns:
            Dict avec statistiques d'import
        """
        try:
            # Lire le fichier Excel
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            created = 0
            updated = 0
            errors = 0
            
            for _, row in df.iterrows():
                try:
                    # Vérifier si le matériau existe déjà
                    code = str(row.get('Code', row.get('code', ''))).strip()
                    
                    if not code:
                        errors += 1
                        continue
                    
                    existing = db.query(Material).filter(Material.code == code).first()
                    
                    # Prix
                    price_eur = Decimal(str(row.get('Prix EUR', row.get('price_eur', 0))))
                    price_lei = row.get('Prix LEI', row.get('price_lei', None))
                    if price_lei is not None and pd.notna(price_lei):
                        price_lei = Decimal(str(price_lei))
                    else:
                        # Calculer automatiquement si non fourni
                        price_lei = PriceCalculator.convert_eur_to_lei(price_eur)
                    
                    if existing:
                        # Mettre à jour
                        existing.name_fr = str(row.get('Nom FR', row.get('name_fr', existing.name_fr)))
                        existing.name_ro = str(row.get('Nom RO', row.get('name_ro', ''))) or None
                        existing.unit = str(row.get('Unité', row.get('unit', existing.unit)))
                        existing.price_eur = price_eur
                        existing.price_lei = price_lei
                        existing.price_date = datetime.utcnow().isoformat()
                        existing.supplier = str(row.get('Fournisseur', row.get('supplier', ''))) or None
                        existing.updated_at = datetime.utcnow().isoformat()
                        
                        updated += 1
                    else:
                        # Créer
                        material = Material(
                            id=uuid.uuid4(),
                            code=code,
                            name_fr=str(row.get('Nom FR', row.get('name_fr', code))),
                            name_ro=str(row.get('Nom RO', row.get('name_ro', ''))) or None,
                            unit=str(row.get('Unité', row.get('unit', 'u'))),
                            price_eur=price_eur,
                            price_lei=price_lei,
                            supplier=str(row.get('Fournisseur', row.get('supplier', ''))) or None,
                        )
                        db.add(material)
                        created += 1
                    
                except Exception as e:
                    print(f"Erreur sur la ligne: {e}")
                    errors += 1
                    continue
            
            # Commit tous les changements
            db.commit()
            
            return {
                "created": created,
                "updated": updated,
                "errors": errors,
                "total": created + updated
            }
        
        except Exception as e:
            db.rollback()
            raise Exception(f"Erreur lors de l'import Excel: {str(e)}")
    
    @staticmethod
    def import_services_from_excel(
        file_path: str,
        db: Session,
        sheet_name: str = "Services"
    ) -> Dict[str, int]:
        """
        Importer des services depuis un fichier Excel
        
        Format attendu :
        - Code | Nom | Unité | Prix Net | Prix Brut
        
        Args:
            file_path: Chemin du fichier Excel
            db: Session de base de données
            sheet_name: Nom de la feuille à lire
            
        Returns:
            Dict avec statistiques d'import
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            created = 0
            updated = 0
            errors = 0
            
            for _, row in df.iterrows():
                try:
                    code = str(row.get('Code', row.get('code', ''))).strip()
                    
                    if not code:
                        errors += 1
                        continue
                    
                    existing = db.query(Service).filter(Service.code == code).first()
                    
                    price_net = Decimal(str(row.get('Prix Net', row.get('price_net', 0))))
                    price_gross = Decimal(str(row.get('Prix Brut', row.get('price_gross', 0))))
                    margin = PriceCalculator.calculate_service_margin(price_net, price_gross)
                    
                    if existing:
                        # Mettre à jour
                        existing.name = str(row.get('Nom', row.get('name', existing.name)))
                        existing.unit = str(row.get('Unité', row.get('unit', existing.unit)))
                        existing.price_net = price_net
                        existing.price_gross = price_gross
                        existing.margin = margin
                        existing.updated_at = datetime.utcnow().isoformat()
                        
                        updated += 1
                    else:
                        # Créer
                        service = Service(
                            id=uuid.uuid4(),
                            code=code,
                            name=str(row.get('Nom', row.get('name', code))),
                            description=str(row.get('Description', row.get('description', ''))) or None,
                            unit=str(row.get('Unité', row.get('unit', 'ft'))),
                            price_net=price_net,
                            price_gross=price_gross,
                            margin=margin,
                        )
                        db.add(service)
                        created += 1
                
                except Exception as e:
                    print(f"Erreur sur la ligne: {e}")
                    errors += 1
                    continue
            
            db.commit()
            
            return {
                "created": created,
                "updated": updated,
                "errors": errors,
                "total": created + updated
            }
        
        except Exception as e:
            db.rollback()
            raise Exception(f"Erreur lors de l'import Excel: {str(e)}")
    
    @staticmethod
    def detect_excel_structure(file_path: str) -> Dict[str, List[str]]:
        """
        Détecter la structure d'un fichier Excel
        
        Args:
            file_path: Chemin du fichier Excel
            
        Returns:
            Dict avec les noms de feuilles et leurs colonnes
        """
        try:
            xls = pd.ExcelFile(file_path)
            structure = {}
            
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=5)
                structure[sheet_name] = list(df.columns)
            
            return structure
        
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du fichier: {str(e)}")
