"""
Module cores pour la Gestion Obligataire
Contient les calculs, modèles de données et configuration
"""

from .bond_calculations import (
    calculate_bond_price,
    calculate_yield_to_maturity,
    calculate_macaulay_duration,
    calculate_modified_duration,
    calculate_convexity,
    calculate_accrued_interest,
    generate_cash_flow_schedule,
    calculate_current_yield
)

from .data_models import (
    Bond,
    BondPosition,
    Portfolio,
    BondType,
    CreditRating,
    BondMetrics
)

from .config import (
    PAGE_CONFIG,
    COLORS,
    DEFAULT_BOND_PARAMS,
    PAYMENT_FREQUENCIES,
    CURRENCIES,
    NUMBER_FORMAT,
    apply_custom_css,
    init_session_state,
    format_number,
    get_app_info
)

__version__ = "1.0.0"
__author__ = "DylaneTrader"

__all__ = [
    # Bond calculations
    'calculate_bond_price',
    'calculate_yield_to_maturity',
    'calculate_macaulay_duration',
    'calculate_modified_duration',
    'calculate_convexity',
    'calculate_accrued_interest',
    'generate_cash_flow_schedule',
    'calculate_current_yield',
    # Data models
    'Bond',
    'BondPosition',
    'Portfolio',
    'BondType',
    'CreditRating',
    'BondMetrics',
    # Config
    'PAGE_CONFIG',
    'COLORS',
    'DEFAULT_BOND_PARAMS',
    'PAYMENT_FREQUENCIES',
    'CURRENCIES',
    'NUMBER_FORMAT',
    'apply_custom_css',
    'init_session_state',
    'format_number',
    'get_app_info',
]
