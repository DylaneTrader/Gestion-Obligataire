"""
Application Streamlit de Gestion Obligataire
Page d'accueil principale
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

from cores.config import PAGE_CONFIG, apply_custom_css, init_session_state, get_app_info
from cores.bond_calculations import (
    calculate_bond_price,
    calculate_yield_to_maturity,
    calculate_macaulay_duration,
    calculate_modified_duration,
    calculate_convexity,
    calculate_current_yield
)
from cores.data_models import Bond, BondType, CreditRating

# Configuration de la page
st.set_page_config(**PAGE_CONFIG)

# Application du CSS personnalisé
apply_custom_css()

# Initialisation de l'état de session
init_session_state()


def main():
    """Fonction principale de la page d'accueil"""
    
    # En-tête
    st.title("📊 Gestion Obligataire")
    st.markdown("### Application avancée d'analyse et de gestion d'obligations")
    
    # Introduction
    st.markdown("""
    <div class="info-box">
        <h4>Bienvenue dans l'application de Gestion Obligataire</h4>
        <p>Cette application vous permet d'analyser des obligations, de calculer leurs métriques financières
        et de gérer un portefeuille obligataire complet.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section des fonctionnalités principales
    st.markdown("---")
    st.header("🎯 Fonctionnalités Principales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Pricing d'Obligations</h3>
            <ul>
                <li>Calcul du prix théorique</li>
                <li>Rendement à l'échéance (YTM)</li>
                <li>Rendement courant</li>
                <li>Analyse de sensibilité</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Métriques de Risque</h3>
            <ul>
                <li>Duration de Macaulay</li>
                <li>Duration modifiée</li>
                <li>Convexité</li>
                <li>Intérêts courus</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>💼 Gestion de Portefeuille</h3>
            <ul>
                <li>Suivi des positions</li>
                <li>Analyse P&L</li>
                <li>Diversification</li>
                <li>Reporting détaillé</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Calculateur rapide
    st.markdown("---")
    st.header("⚡ Calculateur Rapide")
    
    with st.expander("🔍 Calculer le prix d'une obligation", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            face_value = st.number_input(
                "Valeur nominale (€)",
                min_value=100.0,
                max_value=1000000.0,
                value=1000.0,
                step=100.0,
                key="quick_face_value"
            )
            
            coupon_rate = st.slider(
                "Taux du coupon (%)",
                min_value=0.0,
                max_value=15.0,
                value=5.0,
                step=0.25,
                key="quick_coupon"
            ) / 100
            
            years_to_maturity = st.number_input(
                "Années jusqu'à l'échéance",
                min_value=0.5,
                max_value=30.0,
                value=5.0,
                step=0.5,
                key="quick_maturity"
            )
        
        with col2:
            yield_rate = st.slider(
                "Taux de rendement requis (%)",
                min_value=0.0,
                max_value=15.0,
                value=5.0,
                step=0.25,
                key="quick_yield"
            ) / 100
            
            frequency = st.selectbox(
                "Fréquence de paiement",
                options=[1, 2, 4, 12],
                format_func=lambda x: {1: "Annuel", 2: "Semestriel", 4: "Trimestriel", 12: "Mensuel"}[x],
                index=1,
                key="quick_frequency"
            )
        
        if st.button("Calculer", key="quick_calculate"):
            # Calculs
            price = calculate_bond_price(
                face_value, coupon_rate, years_to_maturity, yield_rate, frequency
            )
            
            current_yield = calculate_current_yield(price, face_value, coupon_rate)
            
            mac_duration = calculate_macaulay_duration(
                face_value, coupon_rate, years_to_maturity, yield_rate, frequency
            )
            
            mod_duration = calculate_modified_duration(
                face_value, coupon_rate, years_to_maturity, yield_rate, frequency
            )
            
            convexity = calculate_convexity(
                face_value, coupon_rate, years_to_maturity, yield_rate, frequency
            )
            
            # Affichage des résultats
            st.markdown("---")
            st.subheader("Résultats")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Prix de l'obligation", f"{price:.2f} €")
                st.metric("Rendement courant", f"{current_yield*100:.2f}%")
            
            with col2:
                st.metric("Duration de Macaulay", f"{mac_duration:.4f} ans")
                st.metric("Duration modifiée", f"{mod_duration:.4f}")
            
            with col3:
                premium_discount = ((price - face_value) / face_value) * 100
                st.metric("Prime/Décote", f"{premium_discount:.2f}%")
                st.metric("Convexité", f"{convexity:.4f}")
            
            # Graphique de sensibilité
            st.markdown("---")
            st.subheader("Analyse de Sensibilité au Rendement")
            
            # Variation du rendement de -2% à +2%
            yield_range = [yield_rate + i * 0.001 for i in range(-200, 201, 10)]
            prices = [
                calculate_bond_price(face_value, coupon_rate, years_to_maturity, y, frequency)
                for y in yield_range
            ]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[y * 100 for y in yield_range],
                y=prices,
                mode='lines',
                name='Prix',
                line=dict(color='#1f77b4', width=2)
            ))
            
            # Point actuel
            fig.add_trace(go.Scatter(
                x=[yield_rate * 100],
                y=[price],
                mode='markers',
                name='Point actuel',
                marker=dict(size=12, color='red')
            ))
            
            fig.update_layout(
                title='Prix de l\'obligation vs Rendement',
                xaxis_title='Rendement (%)',
                yaxis_title='Prix (€)',
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Section navigation
    st.markdown("---")
    st.header("📑 Navigation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**📈 Bond Pricing**\n\nAnalysez en détail le pricing et les métriques d'une obligation")
    
    with col2:
        st.info("**💼 Portfolio Analysis**\n\nGérez et analysez votre portefeuille d'obligations")
    
    with col3:
        st.info("**ℹ️ About**\n\nDécouvrez plus d'informations sur l'application")
    
    # Pied de page
    st.markdown("---")
    app_info = get_app_info()
    st.caption(f"**{app_info['name']}** v{app_info['version']} | Développé par {app_info['author']}")


if __name__ == "__main__":
    main()
