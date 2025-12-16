"""
Page d'analyse de portefeuille obligataire
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from cores.config import PAGE_CONFIG, apply_custom_css, init_session_state
from cores.bond_calculations import (
    calculate_bond_price,
    calculate_yield_to_maturity,
    calculate_modified_duration
)
from cores.data_models import Bond, BondPosition, Portfolio, BondType, CreditRating

st.set_page_config(**PAGE_CONFIG)
apply_custom_css()
init_session_state()

st.title("💼 Analyse de Portefeuille")
st.markdown("### Gestion et analyse de votre portefeuille obligataire")

# Initialiser le portefeuille dans la session
if st.session_state.portfolio is None:
    st.session_state.portfolio = Portfolio(name="Mon Portefeuille", currency="EUR")

portfolio = st.session_state.portfolio

# Onglets
tab1, tab2, tab3 = st.tabs([
    "📋 Positions",
    "📊 Analyse",
    "➕ Ajouter Position"
])

# --- TAB 1: POSITIONS ---
with tab1:
    st.header("Positions du Portefeuille")
    
    if len(portfolio.positions) == 0:
        st.info("ℹ️ Votre portefeuille est vide. Ajoutez des positions dans l'onglet 'Ajouter Position'.")
    else:
        # Statistiques globales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Nombre de Positions",
                len(portfolio.positions)
            )
        
        with col2:
            st.metric(
                "Valeur Comptable",
                f"{portfolio.total_book_value():,.2f} €"
            )
        
        with col3:
            market_value = portfolio.total_market_value()
            st.metric(
                "Valeur de Marché",
                f"{market_value:,.2f} €"
            )
        
        with col4:
            pnl_pct = portfolio.total_unrealized_pnl_percent()
            st.metric(
                "P&L Non Réalisé",
                f"{pnl_pct:.2f}%",
                f"{portfolio.total_unrealized_pnl():,.2f} €"
            )
        
        st.markdown("---")
        
        # Tableau des positions
        st.subheader("Détail des Positions")
        
        positions_data = []
        for pos in portfolio.positions:
            positions_data.append({
                "Nom": pos.bond.name,
                "ISIN": pos.bond.isin,
                "Type": pos.bond.bond_type.value,
                "Quantité": pos.quantity,
                "Prix d'Achat": f"{pos.purchase_price:.2f} €",
                "Prix Actuel": f"{pos.current_price:.2f} €" if pos.current_price else "N/A",
                "Valeur Comptable": f"{pos.book_value():,.2f} €",
                "Valeur de Marché": f"{pos.market_value():,.2f} €",
                "P&L": f"{pos.unrealized_pnl():,.2f} €",
                "P&L %": f"{pos.unrealized_pnl_percent():.2f}%",
                "Échéance": pos.bond.maturity_date.strftime("%Y-%m-%d")
            })
        
        df_positions = pd.DataFrame(positions_data)
        st.dataframe(df_positions, use_container_width=True, hide_index=True)
        
        # Options de gestion
        st.markdown("---")
        st.subheader("Gestion des Positions")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            position_to_remove = st.selectbox(
                "Sélectionner une position à supprimer",
                options=[p.bond.isin for p in portfolio.positions],
                format_func=lambda x: next(
                    (p.bond.name for p in portfolio.positions if p.bond.isin == x), x
                )
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("🗑️ Supprimer Position", use_container_width=True):
                portfolio.remove_position(position_to_remove)
                st.success(f"Position {position_to_remove} supprimée!")
                st.rerun()

# --- TAB 2: ANALYSE ---
with tab2:
    st.header("Analyse du Portefeuille")
    
    if len(portfolio.positions) == 0:
        st.info("ℹ️ Ajoutez des positions pour voir l'analyse du portefeuille.")
    else:
        # Répartition par type
        st.subheader("Répartition par Type d'Obligation")
        
        type_allocation = {}
        for pos in portfolio.positions:
            bond_type = pos.bond.bond_type.value
            if bond_type not in type_allocation:
                type_allocation[bond_type] = 0
            type_allocation[bond_type] += pos.market_value()
        
        fig_type = go.Figure(data=[go.Pie(
            labels=list(type_allocation.keys()),
            values=list(type_allocation.values()),
            hole=0.4
        )])
        
        fig_type.update_layout(
            title="Allocation par Type",
            height=400
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.plotly_chart(fig_type, use_container_width=True)
        
        with col2:
            # Tableau de répartition
            allocation_df = pd.DataFrame([
                {
                    "Type": k,
                    "Valeur": f"{v:,.2f} €",
                    "Pourcentage": f"{(v/portfolio.total_market_value())*100:.2f}%"
                }
                for k, v in type_allocation.items()
            ])
            st.dataframe(allocation_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Performance des positions
        st.subheader("Performance des Positions")
        
        performance_data = []
        for pos in portfolio.positions:
            performance_data.append({
                "Nom": pos.bond.name,
                "P&L": pos.unrealized_pnl(),
                "P&L %": pos.unrealized_pnl_percent()
            })
        
        df_perf = pd.DataFrame(performance_data)
        df_perf = df_perf.sort_values("P&L %", ascending=False)
        
        fig_perf = px.bar(
            df_perf,
            x="Nom",
            y="P&L %",
            title="Performance par Position (%)",
            color="P&L %",
            color_continuous_scale=["red", "yellow", "green"],
            color_continuous_midpoint=0
        )
        
        fig_perf.update_layout(height=400)
        st.plotly_chart(fig_perf, use_container_width=True)
        
        st.markdown("---")
        
        # Maturité du portefeuille
        st.subheader("Profil de Maturité")
        
        maturity_data = []
        for pos in portfolio.positions:
            years_to_mat = pos.bond.years_to_maturity()
            maturity_data.append({
                "Nom": pos.bond.name,
                "Années": years_to_mat,
                "Valeur": pos.market_value()
            })
        
        df_maturity = pd.DataFrame(maturity_data)
        
        fig_maturity = px.scatter(
            df_maturity,
            x="Années",
            y="Valeur",
            size="Valeur",
            hover_data=["Nom"],
            title="Distribution par Maturité",
            labels={"Années": "Années jusqu'à l'Échéance", "Valeur": "Valeur de Marché (€)"}
        )
        
        fig_maturity.update_layout(height=400)
        st.plotly_chart(fig_maturity, use_container_width=True)
        
        st.markdown("---")
        
        # Métriques de risque du portefeuille
        st.subheader("Métriques de Risque du Portefeuille")
        
        # Calculer la duration pondérée
        total_value = portfolio.total_market_value()
        weighted_duration = 0
        
        for pos in portfolio.positions:
            if pos.current_price and pos.bond.coupon_rate > 0:
                try:
                    ytm = calculate_yield_to_maturity(
                        pos.current_price,
                        pos.bond.face_value,
                        pos.bond.coupon_rate,
                        pos.bond.years_to_maturity(),
                        pos.bond.frequency
                    )
                    
                    duration = calculate_modified_duration(
                        pos.bond.face_value,
                        pos.bond.coupon_rate,
                        pos.bond.years_to_maturity(),
                        ytm,
                        pos.bond.frequency
                    )
                    
                    weight = pos.market_value() / total_value
                    weighted_duration += duration * weight
                except:
                    pass
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Duration Moyenne Pondérée", f"{weighted_duration:.4f}")
        
        with col2:
            avg_maturity = sum(p.bond.years_to_maturity() * p.market_value() 
                             for p in portfolio.positions) / total_value
            st.metric("Maturité Moyenne", f"{avg_maturity:.2f} ans")
        
        with col3:
            avg_coupon = sum(p.bond.coupon_rate * p.market_value() 
                           for p in portfolio.positions) / total_value
            st.metric("Coupon Moyen", f"{avg_coupon*100:.2f}%")

# --- TAB 3: AJOUTER POSITION ---
with tab3:
    st.header("Ajouter une Nouvelle Position")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Informations sur l'Obligation")
        
        bond_name = st.text_input("Nom de l'Obligation", "Obligation XYZ")
        bond_isin = st.text_input("Code ISIN", "FR0000000000")
        
        face_value = st.number_input(
            "Valeur Nominale (€)",
            min_value=100.0,
            max_value=100000.0,
            value=1000.0,
            step=100.0
        )
        
        coupon_rate = st.number_input(
            "Taux du Coupon (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.25
        ) / 100
        
        frequency = st.selectbox(
            "Fréquence de Paiement",
            options=[1, 2, 4, 12],
            format_func=lambda x: {1: "Annuel", 2: "Semestriel", 
                                   4: "Trimestriel", 12: "Mensuel"}[x],
            index=1
        )
        
        bond_type = st.selectbox(
            "Type d'Obligation",
            options=list(BondType),
            format_func=lambda x: x.value
        )
        
        credit_rating = st.selectbox(
            "Notation de Crédit",
            options=[None] + list(CreditRating),
            format_func=lambda x: "Non noté" if x is None else x.value
        )
        
        issuer = st.text_input("Émetteur", "Société ABC")
    
    with col2:
        st.subheader("Dates et Position")
        
        issue_date = st.date_input(
            "Date d'Émission",
            value=datetime.now() - timedelta(days=365)
        )
        
        maturity_date = st.date_input(
            "Date d'Échéance",
            value=datetime.now() + timedelta(days=5*365)
        )
        
        quantity = st.number_input(
            "Quantité",
            min_value=1,
            max_value=100000,
            value=10,
            step=1
        )
        
        purchase_price = st.number_input(
            "Prix d'Achat (€)",
            min_value=1.0,
            max_value=100000.0,
            value=1000.0,
            step=10.0
        )
        
        purchase_date = st.date_input(
            "Date d'Achat",
            value=datetime.now()
        )
        
        current_price = st.number_input(
            "Prix Actuel (€)",
            min_value=1.0,
            max_value=100000.0,
            value=1000.0,
            step=10.0,
            help="Laissez égal au prix d'achat si inconnu"
        )
    
    # Bouton d'ajout
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn2:
        if st.button("➕ Ajouter au Portefeuille", use_container_width=True, type="primary"):
            # Créer l'obligation
            new_bond = Bond(
                name=bond_name,
                isin=bond_isin,
                face_value=face_value,
                coupon_rate=coupon_rate,
                issue_date=datetime.combine(issue_date, datetime.min.time()),
                maturity_date=datetime.combine(maturity_date, datetime.min.time()),
                frequency=frequency,
                bond_type=bond_type,
                credit_rating=credit_rating,
                issuer=issuer,
                currency="EUR"
            )
            
            # Créer la position
            new_position = BondPosition(
                bond=new_bond,
                quantity=quantity,
                purchase_price=purchase_price,
                purchase_date=datetime.combine(purchase_date, datetime.min.time()),
                current_price=current_price
            )
            
            # Ajouter au portefeuille
            portfolio.add_position(new_position)
            
            st.success(f"✅ Position {bond_name} ajoutée avec succès!")
            st.balloons()
    
    # Aperçu de la position
    with st.expander("👁️ Aperçu de la Position"):
        st.write(f"**Obligation:** {bond_name} ({bond_isin})")
        st.write(f"**Émetteur:** {issuer}")
        st.write(f"**Type:** {bond_type.value}")
        st.write(f"**Valeur Nominale:** {face_value:.2f} €")
        st.write(f"**Coupon:** {coupon_rate*100:.2f}%")
        st.write(f"**Quantité:** {quantity}")
        st.write(f"**Valeur Comptable:** {quantity * purchase_price:,.2f} €")
        st.write(f"**Valeur de Marché:** {quantity * current_price:,.2f} €")
        
        pnl = (current_price - purchase_price) * quantity
        pnl_pct = ((current_price - purchase_price) / purchase_price) * 100
        st.write(f"**P&L:** {pnl:,.2f} € ({pnl_pct:.2f}%)")

# Pied de page
st.markdown("---")
st.caption("**Gestion Obligataire** - Module de Gestion de Portefeuille")
