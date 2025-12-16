"""
Module de calculs obligataires
Contient les formules pour le pricing, le rendement, la duration, etc.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple


def calculate_bond_price(
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    yield_rate: float,
    frequency: int = 2
) -> float:
    """
    Calcule le prix d'une obligation.
    
    Args:
        face_value: Valeur nominale de l'obligation
        coupon_rate: Taux du coupon (annuel)
        years_to_maturity: Années jusqu'à l'échéance
        yield_rate: Taux de rendement requis (annuel)
        frequency: Fréquence des paiements par an (1=annuel, 2=semestriel)
    
    Returns:
        Prix de l'obligation
    """
    if yield_rate == 0:
        # Cas spécial: rendement nul
        coupon_payment = (face_value * coupon_rate) / frequency
        return (coupon_payment * years_to_maturity * frequency) + face_value
    
    n_periods = int(years_to_maturity * frequency)
    coupon_payment = (face_value * coupon_rate) / frequency
    period_yield = yield_rate / frequency
    
    # Prix des coupons (annuité)
    if period_yield != 0:
        pv_coupons = coupon_payment * (1 - (1 + period_yield) ** -n_periods) / period_yield
    else:
        pv_coupons = coupon_payment * n_periods
    
    # Prix de la valeur nominale
    pv_face_value = face_value / ((1 + period_yield) ** n_periods)
    
    return pv_coupons + pv_face_value


def calculate_yield_to_maturity(
    price: float,
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    frequency: int = 2,
    tolerance: float = 0.0001,
    max_iterations: int = 100
) -> float:
    """
    Calcule le rendement à l'échéance (YTM) par méthode de Newton-Raphson.
    
    Args:
        price: Prix actuel de l'obligation
        face_value: Valeur nominale
        coupon_rate: Taux du coupon
        years_to_maturity: Années jusqu'à l'échéance
        frequency: Fréquence des paiements
        tolerance: Tolérance pour la convergence
        max_iterations: Nombre maximum d'itérations
    
    Returns:
        Rendement à l'échéance (YTM)
    """
    # Estimation initiale
    ytm = coupon_rate
    
    for _ in range(max_iterations):
        calculated_price = calculate_bond_price(
            face_value, coupon_rate, years_to_maturity, ytm, frequency
        )
        
        if abs(calculated_price - price) < tolerance:
            return ytm
        
        # Calcul de la dérivée (approximation numérique)
        delta = 0.0001
        price_up = calculate_bond_price(
            face_value, coupon_rate, years_to_maturity, ytm + delta, frequency
        )
        derivative = (price_up - calculated_price) / delta
        
        if derivative == 0:
            break
        
        # Mise à jour selon Newton-Raphson
        ytm = ytm - (calculated_price - price) / derivative
    
    return ytm


def calculate_macaulay_duration(
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    yield_rate: float,
    frequency: int = 2
) -> float:
    """
    Calcule la duration de Macaulay.
    
    Args:
        face_value: Valeur nominale
        coupon_rate: Taux du coupon
        years_to_maturity: Années jusqu'à l'échéance
        yield_rate: Taux de rendement
        frequency: Fréquence des paiements
    
    Returns:
        Duration de Macaulay (en années)
    """
    n_periods = int(years_to_maturity * frequency)
    coupon_payment = (face_value * coupon_rate) / frequency
    period_yield = yield_rate / frequency
    
    price = calculate_bond_price(
        face_value, coupon_rate, years_to_maturity, yield_rate, frequency
    )
    
    weighted_cash_flows = 0
    
    for t in range(1, n_periods + 1):
        cash_flow = coupon_payment
        if t == n_periods:
            cash_flow += face_value
        
        pv_cash_flow = cash_flow / ((1 + period_yield) ** t)
        time_in_years = t / frequency
        weighted_cash_flows += time_in_years * pv_cash_flow
    
    return weighted_cash_flows / price


def calculate_modified_duration(
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    yield_rate: float,
    frequency: int = 2
) -> float:
    """
    Calcule la duration modifiée.
    
    Args:
        face_value: Valeur nominale
        coupon_rate: Taux du coupon
        years_to_maturity: Années jusqu'à l'échéance
        yield_rate: Taux de rendement
        frequency: Fréquence des paiements
    
    Returns:
        Duration modifiée
    """
    mac_duration = calculate_macaulay_duration(
        face_value, coupon_rate, years_to_maturity, yield_rate, frequency
    )
    
    return mac_duration / (1 + yield_rate / frequency)


def calculate_convexity(
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    yield_rate: float,
    frequency: int = 2
) -> float:
    """
    Calcule la convexité de l'obligation.
    
    Args:
        face_value: Valeur nominale
        coupon_rate: Taux du coupon
        years_to_maturity: Années jusqu'à l'échéance
        yield_rate: Taux de rendement
        frequency: Fréquence des paiements
    
    Returns:
        Convexité
    """
    n_periods = int(years_to_maturity * frequency)
    coupon_payment = (face_value * coupon_rate) / frequency
    period_yield = yield_rate / frequency
    
    price = calculate_bond_price(
        face_value, coupon_rate, years_to_maturity, yield_rate, frequency
    )
    
    convexity_sum = 0
    
    for t in range(1, n_periods + 1):
        cash_flow = coupon_payment
        if t == n_periods:
            cash_flow += face_value
        
        pv_cash_flow = cash_flow / ((1 + period_yield) ** t)
        convexity_sum += (t * (t + 1)) * pv_cash_flow
    
    return convexity_sum / (price * (1 + period_yield) ** 2 * frequency ** 2)


def calculate_accrued_interest(
    face_value: float,
    coupon_rate: float,
    last_coupon_date: datetime,
    settlement_date: datetime,
    frequency: int = 2
) -> float:
    """
    Calcule les intérêts courus.
    
    Args:
        face_value: Valeur nominale
        coupon_rate: Taux du coupon
        last_coupon_date: Date du dernier coupon
        settlement_date: Date de règlement
        frequency: Fréquence des paiements
    
    Returns:
        Intérêts courus
    """
    days_since_last_coupon = (settlement_date - last_coupon_date).days
    days_in_period = 365 / frequency
    
    coupon_payment = (face_value * coupon_rate) / frequency
    accrued = coupon_payment * (days_since_last_coupon / days_in_period)
    
    return accrued


def generate_cash_flow_schedule(
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    frequency: int = 2,
    start_date: datetime = None
) -> List[Tuple[datetime, float]]:
    """
    Génère le calendrier des flux de trésorerie.
    
    Args:
        face_value: Valeur nominale
        coupon_rate: Taux du coupon
        years_to_maturity: Années jusqu'à l'échéance
        frequency: Fréquence des paiements
        start_date: Date de début (défaut: aujourd'hui)
    
    Returns:
        Liste de tuples (date, montant)
    """
    if start_date is None:
        start_date = datetime.now()
    
    n_periods = int(years_to_maturity * frequency)
    coupon_payment = (face_value * coupon_rate) / frequency
    months_between = 12 // frequency
    
    schedule = []
    
    for i in range(1, n_periods + 1):
        payment_date = start_date + timedelta(days=int(i * 365 / frequency))
        amount = coupon_payment
        
        if i == n_periods:
            amount += face_value
        
        schedule.append((payment_date, amount))
    
    return schedule


def calculate_current_yield(
    price: float,
    face_value: float,
    coupon_rate: float
) -> float:
    """
    Calcule le rendement courant.
    
    Args:
        price: Prix actuel
        face_value: Valeur nominale
        coupon_rate: Taux du coupon
    
    Returns:
        Rendement courant
    """
    annual_coupon = face_value * coupon_rate
    return annual_coupon / price
