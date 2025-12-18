"""
Page d'analyse et de pricing d'obligations
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

from cores.config import PAGE_CONFIG, apply_custom_css, PAYMENT_FREQUENCIES
from cores.bond_calculations import (
    calculate_bond_price,
    calculate_yield_to_maturity,
    calculate_macaulay_duration,
    calculate_modified_duration,
    calculate_convexity,
    calculate_current_yield,
    generate_cash_flow_schedule,
    calculate_accrued_interest
)
from cores.data_models import Bond, BondType, CreditRating

st.set_page_config(**PAGE_CONFIG)
apply_custom_css()

st.title("📈 Pricing d'Obligations")
st.markdown("### Analyse détaillée et calcul des métriques obligataires")

# Onglets pour différentes fonctionnalités
tab1, tab2, tab3, tab4 = st.tabs([
    "💰 Calcul de Prix",
    "📊 Analyse Complète",
    "📉 Courbe de Prix",
    "💸 Flux de Trésorerie"
])

# --- TAB 1: CALCUL DE PRIX ---
with tab1:
    st.header("Calculateur de Prix d'Obligation")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Paramètres de l'Obligation")
        
        face_value = st.number_input(
            "Valeur Nominale (€)",
            min_value=100.0,
            max_value=10000000.0,
            value=1000.0,
            step=100.0,
            help="La valeur de remboursement à l'échéance"
        )
        
        coupon_rate = st.number_input(
            "Taux du Coupon (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.25,
            help="Taux d'intérêt annuel de l'obligation"
        ) / 100
        
        years_to_maturity = st.number_input(
            "Années jusqu'à l'Échéance",
            min_value=0.25,
            max_value=50.0,
            value=5.0,
            step=0.25,
            help="Durée restante avant l'échéance"
        )
        
        yield_rate = st.number_input(
            "Taux de Rendement Requis (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.25,
            help="Taux de rendement exigé par le marché"
        ) / 100
        
        frequency = st.selectbox(
            "Fréquence de Paiement",
            options=list(PAYMENT_FREQUENCIES.keys()),
            format_func=lambda x: PAYMENT_FREQUENCIES[x],
            index=1,
            help="Fréquence des paiements de coupons"
        )
    
    with col2:
        st.subheader("Résultats de Pricing")
        
        # Calcul du prix
        price = calculate_bond_price(
            face_value, coupon_rate, years_to_maturity, yield_rate, frequency
        )
        
        # Calcul du rendement courant
        current_yield = calculate_current_yield(price, face_value, coupon_rate)
        
        # Premium/Discount
        premium_discount = price - face_value
        premium_discount_pct = (premium_discount / face_value) * 100
        
        # Affichage des métriques
        st.metric(
            "Prix de l'Obligation",
            f"{price:.2f} €",
            f"{premium_discount:.2f} €"
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Valeur Nominale", f"{face_value:.2f} €")
            st.metric("Rendement Courant", f"{current_yield*100:.2f}%")
        
        with col_b:
            status = "Prime" if premium_discount > 0 else "Décote" if premium_discount < 0 else "Au pair"
            st.metric("Statut", status)
            st.metric("Prime/Décote", f"{premium_discount_pct:.2f}%")
        
        # Information supplémentaire
        st.info(f"""
        **Interprétation:**
        - Coupon total annuel: {face_value * coupon_rate:.2f} €
        - Paiement par période: {(face_value * coupon_rate) / frequency:.2f} €
        - Nombre de paiements: {int(years_to_maturity * frequency)}
        """)
        
        # Comparaison coupon vs yield
        if coupon_rate > yield_rate:
            st.success("✅ L'obligation se négocie **à prime** (coupon > rendement)")
        elif coupon_rate < yield_rate:
            st.warning("⚠️ L'obligation se négocie **à décote** (coupon < rendement)")
        else:
            st.info("ℹ️ L'obligation se négocie **au pair** (coupon = rendement)")

# --- TAB 2: ANALYSE COMPLÈTE ---
with tab2:
    st.header("Analyse Complète de l'Obligation")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Paramètres")
        
        face_value_full = st.number_input(
            "Valeur Nominale (€)",
            min_value=100.0,
            max_value=10000000.0,
            value=1000.0,
            step=100.0,
            key="full_face"
        )
        
        coupon_rate_full = st.number_input(
            "Taux du Coupon (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.25,
            key="full_coupon"
        ) / 100
        
        years_to_maturity_full = st.number_input(
            "Années jusqu'à l'Échéance",
            min_value=0.25,
            max_value=50.0,
            value=5.0,
            step=0.25,
            key="full_years"
        )
        
        yield_rate_full = st.number_input(
            "Taux de Rendement (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.25,
            key="full_yield"
        ) / 100
        
        frequency_full = st.selectbox(
            "Fréquence de Paiement",
            options=list(PAYMENT_FREQUENCIES.keys()),
            format_func=lambda x: PAYMENT_FREQUENCIES[x],
            index=1,
            key="full_freq"
        )
    
    with col2:
        st.subheader("Métriques Calculées")
        
        # Tous les calculs
        price_full = calculate_bond_price(
            face_value_full, coupon_rate_full, years_to_maturity_full,
            yield_rate_full, frequency_full
        )
        
        current_yield_full = calculate_current_yield(
            price_full, face_value_full, coupon_rate_full
        )
        
        mac_duration = calculate_macaulay_duration(
            face_value_full, coupon_rate_full, years_to_maturity_full,
            yield_rate_full, frequency_full
        )
        
        mod_duration = calculate_modified_duration(
            face_value_full, coupon_rate_full, years_to_maturity_full,
            yield_rate_full, frequency_full
        )
        
        convexity = calculate_convexity(
            face_value_full, coupon_rate_full, years_to_maturity_full,
            yield_rate_full, frequency_full
        )
        
        # Affichage dans un tableau
        metrics_data = {
            "Métrique": [
                "Prix de l'Obligation",
                "Rendement Courant",
                "Rendement à l'Échéance",
                "Duration de Macaulay",
                "Duration Modifiée",
                "Convexité"
            ],
            "Valeur": [
                f"{price_full:.2f} €",
                f"{current_yield_full*100:.2f}%",
                f"{yield_rate_full*100:.2f}%",
                f"{mac_duration:.4f} ans",
                f"{mod_duration:.4f}",
                f"{convexity:.4f}"
            ]
        }
        
        df_metrics = pd.DataFrame(metrics_data)
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)
        
        # Estimation de sensibilité
        st.markdown("---")
        st.subheader("Sensibilité au Rendement")
        
        yield_change = st.slider(
            "Variation du rendement (points de base)",
            min_value=-200,
            max_value=200,
            value=0,
            step=10,
            key="yield_change"
        )
        
        yield_change_decimal = yield_change / 10000
        
        # Estimation par duration
        price_change_duration = -mod_duration * yield_change_decimal * price_full
        
        # Estimation avec convexité
        price_change_convexity = (
            -mod_duration * yield_change_decimal * price_full +
            0.5 * convexity * (yield_change_decimal ** 2) * price_full
        )
        
        # Prix exact
        new_yield = yield_rate_full + yield_change_decimal
        price_exact = calculate_bond_price(
            face_value_full, coupon_rate_full, years_to_maturity_full,
            new_yield, frequency_full
        )
        price_change_exact = price_exact - price_full
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric(
                "Approx. Duration",
                f"{price_full + price_change_duration:.2f} €",
                f"{price_change_duration:.2f} €"
            )
        
        with col_b:
            st.metric(
                "Approx. Duration+Convexité",
                f"{price_full + price_change_convexity:.2f} €",
                f"{price_change_convexity:.2f} €"
            )
        
        with col_c:
            st.metric(
                "Prix Exact",
                f"{price_exact:.2f} €",
                f"{price_change_exact:.2f} €"
            )

# --- TAB 3: COURBE DE PRIX ---
with tab3:
    st.header("Courbes d'Analyse de Prix")
    
    # Paramètres pour les courbes
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Paramètres de Base")
        
        face_value_curve = st.number_input(
            "Valeur Nominale (€)",
            min_value=100.0,
            value=1000.0,
            step=100.0,
            key="curve_face"
        )
        
        coupon_rate_curve = st.number_input(
            "Taux du Coupon (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            key="curve_coupon"
        ) / 100
        
        years_to_maturity_curve = st.number_input(
            "Années jusqu'à l'Échéance",
            min_value=1.0,
            max_value=30.0,
            value=10.0,
            step=1.0,
            key="curve_years"
        )
        
        frequency_curve = st.selectbox(
            "Fréquence",
            options=list(PAYMENT_FREQUENCIES.keys()),
            format_func=lambda x: PAYMENT_FREQUENCIES[x],
            index=1,
            key="curve_freq"
        )
        
        curve_type = st.radio(
            "Type de Courbe",
            ["Prix vs Rendement", "Prix vs Maturité", "Prix vs Coupon"],
            key="curve_type"
        )
    
    with col2:
        st.subheader("Visualisation")
        
        fig = go.Figure()
        
        if curve_type == "Prix vs Rendement":
            # Courbe prix vs rendement
            yields = np.linspace(0.01, 0.15, 50)
            prices = [
                calculate_bond_price(
                    face_value_curve, coupon_rate_curve,
                    years_to_maturity_curve, y, frequency_curve
                )
                for y in yields
            ]
            
            fig.add_trace(go.Scatter(
                x=yields * 100,
                y=prices,
                mode='lines',
                name='Prix',
                line=dict(color='#1f77b4', width=3)
            ))
            
            # Ligne de la valeur nominale
            fig.add_hline(
                y=face_value_curve,
                line_dash="dash",
                line_color="red",
                annotation_text="Valeur Nominale"
            )
            
            fig.update_layout(
                title='Prix de l\'Obligation en fonction du Rendement',
                xaxis_title='Rendement (%)',
                yaxis_title='Prix (€)',
                hovermode='x unified'
            )
        
        elif curve_type == "Prix vs Maturité":
            # Courbe prix vs maturité
            maturities = np.linspace(0.5, 30, 50)
            
            # Plusieurs rendements
            for ytm in [0.03, 0.05, 0.07]:
                prices = [
                    calculate_bond_price(
                        face_value_curve, coupon_rate_curve,
                        m, ytm, frequency_curve
                    )
                    for m in maturities
                ]
                
                fig.add_trace(go.Scatter(
                    x=maturities,
                    y=prices,
                    mode='lines',
                    name=f'YTM = {ytm*100:.0f}%',
                    line=dict(width=2)
                ))
            
            fig.add_hline(
                y=face_value_curve,
                line_dash="dash",
                line_color="red",
                annotation_text="Valeur Nominale"
            )
            
            fig.update_layout(
                title='Prix de l\'Obligation en fonction de la Maturité',
                xaxis_title='Années jusqu\'à l\'Échéance',
                yaxis_title='Prix (€)',
                hovermode='x unified'
            )
        
        else:  # Prix vs Coupon
            # Courbe prix vs coupon
            coupons = np.linspace(0.01, 0.15, 50)
            
            # Plusieurs rendements
            for ytm in [0.03, 0.05, 0.07]:
                prices = [
                    calculate_bond_price(
                        face_value_curve, c,
                        years_to_maturity_curve, ytm, frequency_curve
                    )
                    for c in coupons
                ]
                
                fig.add_trace(go.Scatter(
                    x=coupons * 100,
                    y=prices,
                    mode='lines',
                    name=f'YTM = {ytm*100:.0f}%',
                    line=dict(width=2)
                ))
            
            fig.add_hline(
                y=face_value_curve,
                line_dash="dash",
                line_color="red",
                annotation_text="Valeur Nominale"
            )
            
            fig.update_layout(
                title='Prix de l\'Obligation en fonction du Taux de Coupon',
                xaxis_title='Taux de Coupon (%)',
                yaxis_title='Prix (€)',
                hovermode='x unified'
            )
        
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 4: FLUX DE TRÉSORERIE ---
with tab4:
    st.header("Analyse des Flux de Trésorerie")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Paramètres")
        
        face_value_cf = st.number_input(
            "Valeur Nominale (€)",
            min_value=100.0,
            value=1000.0,
            step=100.0,
            key="cf_face"
        )
        
        coupon_rate_cf = st.number_input(
            "Taux du Coupon (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            key="cf_coupon"
        ) / 100
        
        years_to_maturity_cf = st.number_input(
            "Années jusqu'à l'Échéance",
            min_value=1.0,
            max_value=30.0,
            value=5.0,
            step=1.0,
            key="cf_years"
        )
        
        frequency_cf = st.selectbox(
            "Fréquence",
            options=list(PAYMENT_FREQUENCIES.keys()),
            format_func=lambda x: PAYMENT_FREQUENCIES[x],
            index=1,
            key="cf_freq"
        )
        
        yield_rate_cf = st.number_input(
            "Taux d'Actualisation (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            key="cf_yield"
        ) / 100
    
    with col2:
        st.subheader("Calendrier des Flux")
        
        # Génération du calendrier
        cash_flows = generate_cash_flow_schedule(
            face_value_cf, coupon_rate_cf, years_to_maturity_cf,
            frequency_cf, datetime.now()
        )
        
        # Création du DataFrame
        cf_data = []
        for i, (date, amount) in enumerate(cash_flows, 1):
            period_yield = yield_rate_cf / frequency_cf
            pv = amount / ((1 + period_yield) ** i)
            cf_data.append({
                "Période": i,
                "Date": date.strftime("%Y-%m-%d"),
                "Flux (€)": f"{amount:.2f}",
                "Valeur Actuelle (€)": f"{pv:.2f}"
            })
        
        df_cf = pd.DataFrame(cf_data)
        st.dataframe(df_cf, use_container_width=True, hide_index=True)
        
        # Graphique des flux
        st.markdown("---")
        
        amounts = [float(row["Flux (€)"]) for row in cf_data]
        pvs = [float(row["Valeur Actuelle (€)"]) for row in cf_data]
        periods = [row["Période"] for row in cf_data]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=periods,
            y=amounts,
            name='Flux Nominal',
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            x=periods,
            y=pvs,
            name='Valeur Actuelle',
            marker_color='darkblue'
        ))
        
        fig.update_layout(
            title='Flux de Trésorerie et Valeurs Actuelles',
            xaxis_title='Période',
            yaxis_title='Montant (€)',
            barmode='group',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Résumé
        total_cf = sum(amounts)
        total_pv = sum(pvs)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Total des Flux", f"{total_cf:.2f} €")
        with col_b:
            st.metric("Total Valeur Actuelle", f"{total_pv:.2f} €")

# Pied de page
st.markdown("---")
st.caption("**Gestion Obligataire** - Module de Pricing d'Obligations")
