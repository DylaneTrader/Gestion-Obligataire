"""
Configuration de l'application
"""

import streamlit as st
from typing import Dict, Any


# Configuration de la page Streamlit
PAGE_CONFIG = {
    "page_title": "Gestion Obligataire",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Thème de couleurs
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ff9800",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

# Paramètres par défaut pour les obligations
DEFAULT_BOND_PARAMS = {
    "face_value": 1000.0,
    "coupon_rate": 0.05,
    "years_to_maturity": 5.0,
    "yield_rate": 0.05,
    "frequency": 2
}

# Options de fréquence de paiement
PAYMENT_FREQUENCIES = {
    1: "Annuel",
    2: "Semestriel",
    4: "Trimestriel",
    12: "Mensuel"
}

# Devises supportées
CURRENCIES = ["FCFA", "EUR", "USD", "GBP", "CHF", "JPY"]

# Format de nombres
NUMBER_FORMAT = {
    "price": "{:,.2f}",
    "percentage": "{:.2f}%",
    "currency": "{:,.2f} FCFA",
    "duration": "{:.4f}",
    "convexity": "{:.4f}"
}


def apply_custom_css():
    """Applique le CSS personnalisé à l'application"""
    st.markdown("""
        <style>
        .main {
            padding: 0rem 1rem;
        }
        
        .stMetric {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .metric-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #1f77b4;
            color: white;
        }
        
        .stButton>button:hover {
            background-color: #145a8a;
            color: white;
        }
        
        h1 {
            color: #1f77b4;
            padding-bottom: 10px;
            border-bottom: 2px solid #1f77b4;
        }
        
        h2 {
            color: #343a40;
            margin-top: 20px;
        }
        
        h3 {
            color: #495057;
        }
        
        .dataframe {
            font-size: 14px;
        }
        
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        
        div[data-testid="stExpander"] {
            background-color: #ffffff;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        }
        
        .info-box {
            padding: 15px;
            border-radius: 5px;
            background-color: #e3f2fd;
            border-left: 4px solid #2196F3;
            margin: 10px 0;
        }
        
        .warning-box {
            padding: 15px;
            border-radius: 5px;
            background-color: #fff3e0;
            border-left: 4px solid #ff9800;
            margin: 10px 0;
        }
        
        .success-box {
            padding: 15px;
            border-radius: 5px;
            background-color: #e8f5e9;
            border-left: 4px solid #4caf50;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialise l'état de session Streamlit"""
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = None
    
    if 'bonds' not in st.session_state:
        st.session_state.bonds = []
    
    if 'calculation_history' not in st.session_state:
        st.session_state.calculation_history = []


def format_number(value: float, format_type: str = "price") -> str:
    """Formate un nombre selon le type spécifié"""
    if format_type in NUMBER_FORMAT:
        return NUMBER_FORMAT[format_type].format(value)
    return str(value)


def get_app_info() -> Dict[str, Any]:
    """Retourne les informations sur l'application"""
    return {
        "name": "Gestion Obligataire",
        "version": "1.0.0",
        "description": "Application avancée de gestion et d'analyse d'obligations",
        "author": "DylaneTrader",
        "features": [
            "Calcul du prix des obligations",
            "Rendement à l'échéance (YTM)",
            "Duration de Macaulay et modifiée",
            "Convexité",
            "Gestion de portefeuille",
            "Analyse de sensibilité",
            "Visualisation des flux de trésorerie"
        ]
    }
