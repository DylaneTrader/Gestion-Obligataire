"""
Modèles de données pour la gestion obligataire
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class BondType(Enum):
    """Types d'obligations"""
    GOVERNMENT = "Obligation d'État"
    CORPORATE = "Obligation d'entreprise"
    MUNICIPAL = "Obligation municipale"
    CONVERTIBLE = "Obligation convertible"
    ZERO_COUPON = "Obligation zéro coupon"


class CreditRating(Enum):
    """Notations de crédit"""
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"
    CC = "CC"
    C = "C"
    D = "D"


@dataclass
class Bond:
    """Classe représentant une obligation"""
    name: str
    isin: str
    face_value: float
    coupon_rate: float
    issue_date: datetime
    maturity_date: datetime
    frequency: int = 2  # Paiements par an
    bond_type: BondType = BondType.CORPORATE
    credit_rating: Optional[CreditRating] = None
    issuer: str = ""
    currency: str = "EUR"
    
    def years_to_maturity(self, from_date: datetime = None) -> float:
        """Calcule les années jusqu'à l'échéance"""
        if from_date is None:
            from_date = datetime.now()
        
        days_to_maturity = (self.maturity_date - from_date).days
        return days_to_maturity / 365.25
    
    def is_active(self) -> bool:
        """Vérifie si l'obligation est toujours active"""
        return datetime.now() < self.maturity_date


@dataclass
class BondPosition:
    """Position sur une obligation dans un portefeuille"""
    bond: Bond
    quantity: int
    purchase_price: float
    purchase_date: datetime
    current_price: Optional[float] = None
    
    def market_value(self) -> float:
        """Calcule la valeur de marché actuelle"""
        price = self.current_price if self.current_price else self.purchase_price
        return self.quantity * price
    
    def book_value(self) -> float:
        """Calcule la valeur comptable"""
        return self.quantity * self.purchase_price
    
    def unrealized_pnl(self) -> float:
        """Calcule le P&L non réalisé"""
        if self.current_price is None:
            return 0.0
        return (self.current_price - self.purchase_price) * self.quantity
    
    def unrealized_pnl_percent(self) -> float:
        """Calcule le P&L non réalisé en pourcentage"""
        if self.current_price is None:
            return 0.0
        return ((self.current_price - self.purchase_price) / self.purchase_price) * 100


@dataclass
class Portfolio:
    """Portefeuille d'obligations"""
    name: str
    positions: List[BondPosition] = field(default_factory=list)
    currency: str = "EUR"
    
    def add_position(self, position: BondPosition):
        """Ajoute une position au portefeuille"""
        self.positions.append(position)
    
    def remove_position(self, isin: str):
        """Retire une position du portefeuille"""
        self.positions = [p for p in self.positions if p.bond.isin != isin]
    
    def total_market_value(self) -> float:
        """Calcule la valeur de marché totale du portefeuille"""
        return sum(p.market_value() for p in self.positions)
    
    def total_book_value(self) -> float:
        """Calcule la valeur comptable totale du portefeuille"""
        return sum(p.book_value() for p in self.positions)
    
    def total_unrealized_pnl(self) -> float:
        """Calcule le P&L total non réalisé"""
        return sum(p.unrealized_pnl() for p in self.positions)
    
    def total_unrealized_pnl_percent(self) -> float:
        """Calcule le P&L total non réalisé en pourcentage"""
        book_value = self.total_book_value()
        if book_value == 0:
            return 0.0
        return (self.total_unrealized_pnl() / book_value) * 100
    
    def get_position_by_isin(self, isin: str) -> Optional[BondPosition]:
        """Récupère une position par son ISIN"""
        for position in self.positions:
            if position.bond.isin == isin:
                return position
        return None
    
    def get_positions_by_type(self, bond_type: BondType) -> List[BondPosition]:
        """Récupère toutes les positions d'un type donné"""
        return [p for p in self.positions if p.bond.bond_type == bond_type]
    
    def get_positions_by_rating(self, rating: CreditRating) -> List[BondPosition]:
        """Récupère toutes les positions avec une notation donnée"""
        return [p for p in self.positions if p.bond.credit_rating == rating]


@dataclass
class BondMetrics:
    """Métriques calculées pour une obligation"""
    bond: Bond
    price: float
    yield_to_maturity: float
    current_yield: float
    macaulay_duration: float
    modified_duration: float
    convexity: float
    calculation_date: datetime = field(default_factory=datetime.now)
