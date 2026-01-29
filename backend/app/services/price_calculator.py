"""
Service de calcul de prix
Logique métier pour calculer les prix des articles et compositions
"""

from decimal import Decimal
from typing import List, Dict
from sqlalchemy.orm import Session

from app.models.material import Material
from app.models.article import Article, ArticleMaterial
from app.models.composition import Composition, CompositionItem, CompositionItemType
from app.config import settings


class PriceCalculator:
    """Service de calcul automatique des prix"""
    
    @staticmethod
    def calculate_article_price(article: Article, db: Session) -> Dict[str, Decimal]:
        """
        Calculer le prix total d'un article
        
        Prix = (Coût matériaux + Coût MO) × (1 + overhead) × (1 + margin)
        
        Args:
            article: Article à calculer
            db: Session de base de données
            
        Returns:
            Dict avec material_cost, total_cost, total_price
        """
        # Calculer le coût des matériaux
        material_cost = Decimal('0.00')
        
        for am in article.materials:
            material = db.query(Material).filter(Material.id == am.material_id).first()
            if material:
                # Quantité avec perte
                quantity_with_waste = am.quantity * (1 + am.waste_percent)
                # Coût = prix × quantité
                cost = material.price_eur * quantity_with_waste
                material_cost += cost
        
        # Coût total (matériaux + main d'œuvre)
        total_cost = material_cost + article.labor_cost
        
        # Prix de vente = coût × (1 + overhead) × (1 + margin)
        price_with_overhead = total_cost * (1 + article.overhead)
        total_price = price_with_overhead * (1 + article.margin)
        
        return {
            "material_cost": round(material_cost, 2),
            "total_cost": round(total_cost, 2),
            "total_price": round(total_price, 2)
        }
    
    @staticmethod
    def calculate_composition_price(composition: Composition, db: Session) -> Dict[str, Decimal]:
        """
        Calculer le prix total d'une composition
        
        Args:
            composition: Composition à calculer
            db: Session de base de données
            
        Returns:
            Dict avec total_cost, total_price
        """
        total_cost = Decimal('0.00')
        
        for item in composition.items:
            if item.item_type == CompositionItemType.MATERIAL:
                # Récupérer le matériau
                material = db.query(Material).filter(Material.id == item.item_id).first()
                if material:
                    cost = material.price_eur * item.quantity
                    total_cost += cost
            
            elif item.item_type == CompositionItemType.ARTICLE:
                # Récupérer l'article
                article = db.query(Article).filter(Article.id == item.item_id).first()
                if article:
                    # Utiliser le prix total de l'article
                    cost = article.total_price * item.quantity
                    total_cost += cost
        
        # Prix de vente = coût × (1 + overhead) × (1 + margin)
        price_with_overhead = total_cost * (1 + composition.overhead)
        total_price = price_with_overhead * (1 + composition.margin)
        
        return {
            "total_cost": round(total_cost, 2),
            "total_price": round(total_price, 2)
        }
    
    @staticmethod
    def calculate_service_margin(price_net: Decimal, price_gross: Decimal) -> Decimal:
        """
        Calculer la marge d'un service
        
        Args:
            price_net: Prix net (coût)
            price_gross: Prix brut (vente)
            
        Returns:
            Marge en valeur absolue
        """
        return round(price_gross - price_net, 2)
    
    @staticmethod
    def convert_eur_to_lei(amount_eur: Decimal) -> Decimal:
        """
        Convertir EUR vers LEI
        
        Args:
            amount_eur: Montant en EUR
            
        Returns:
            Montant en LEI
        """
        rate = Decimal(str(settings.EUR_LEI_RATE))
        return round(amount_eur * rate, 2)
    
    @staticmethod
    def convert_lei_to_eur(amount_lei: Decimal) -> Decimal:
        """
        Convertir LEI vers EUR
        
        Args:
            amount_lei: Montant en LEI
            
        Returns:
            Montant en EUR
        """
        rate = Decimal(str(settings.EUR_LEI_RATE))
        return round(amount_lei / rate, 2)
