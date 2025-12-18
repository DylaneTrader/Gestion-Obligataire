"""
Page d'analyse des Valeurs Liquidatives (VL)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from cores.config import PAGE_CONFIG, apply_custom_css

st.set_page_config(**PAGE_CONFIG)
apply_custom_css()

st.title("📈 Valeurs Liquidatives")
st.markdown("### Analyse des valeurs liquidatives des FCP")

# Chargement des données
st.header("📂 Chargement des Données")

uploaded_file = st.file_uploader(
    "Charger un fichier Excel avec les données de VL",
    type=['xlsx', 'xls'],
    help="Le fichier doit contenir les colonnes: FCP, Date, VL"
)

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        
        if all(col in df.columns for col in ['FCP', 'Date', 'VL']):
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            
            # Filtre FCP sans sélection par défaut
            st.markdown("---")
            st.header("🔍 Filtres")
            
            fcp_list = sorted(df['FCP'].unique().tolist())
            
            st.markdown("""
            <div class="info-box">
                <p><strong>Sélection FCP :</strong> Aucune sélection = Tous les FCP analysés</p>
            </div>
            """, unsafe_allow_html=True)
            
            selected_fcps = st.multiselect(
                "Sélectionner un ou plusieurs FCP (laisser vide pour tous les FCP)",
                options=fcp_list,
                default=[],
                help="Laissez vide pour analyser tous les FCP"
            )
            
            # Filtrer les données
            if len(selected_fcps) == 0:
                # Aucune sélection = tous les FCP
                df_filtered = df.copy()
                filter_text = "Tous les FCP"
            else:
                # FCP sélectionnés
                df_filtered = df[df['FCP'].isin(selected_fcps)].copy()
                filter_text = ", ".join(selected_fcps)
            
            # Afficher les données filtrées
            st.markdown("---")
            st.subheader(f"Analyse des VL - {filter_text}")
            
            # Métriques globales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                nb_fcp = df_filtered['FCP'].nunique()
                st.metric("Nombre de FCP", nb_fcp)
            
            with col2:
                first_date = df_filtered['Date'].min()
                st.metric("Première Date", first_date.strftime("%Y-%m-%d"))
            
            with col3:
                last_date = df_filtered['Date'].max()
                st.metric("Dernière Date", last_date.strftime("%Y-%m-%d"))
            
            with col4:
                nb_obs = len(df_filtered)
                st.metric("Nombre d'Observations", f"{nb_obs:,}")
            
            # Onglets d'analyse
            st.markdown("---")
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Évolution des VL",
                "📈 Performance",
                "📉 Analyse de Risque",
                "📋 Données Détaillées"
            ])
            
            # --- TAB 1: ÉVOLUTION DES VL ---
            with tab1:
                st.subheader("Évolution des Valeurs Liquidatives")
                
                # Graphique d'évolution
                fig_vl = go.Figure()
                
                if len(selected_fcps) == 0 or len(selected_fcps) > 1:
                    # Plusieurs FCP: une ligne par FCP
                    for fcp in df_filtered['FCP'].unique():
                        df_fcp = df_filtered[df_filtered['FCP'] == fcp]
                        fig_vl.add_trace(go.Scatter(
                            x=df_fcp['Date'],
                            y=df_fcp['VL'],
                            name=fcp,
                            mode='lines+markers',
                            line=dict(width=2)
                        ))
                else:
                    # Un seul FCP
                    fig_vl.add_trace(go.Scatter(
                        x=df_filtered['Date'],
                        y=df_filtered['VL'],
                        name=selected_fcps[0],
                        mode='lines+markers',
                        line=dict(color='steelblue', width=3),
                        fill='tozeroy',
                        fillcolor='rgba(70, 130, 180, 0.2)'
                    ))
                
                fig_vl.update_layout(
                    title=f'Évolution des VL - {filter_text}',
                    xaxis_title='Date',
                    yaxis_title='Valeur Liquidative (FCFA)',
                    hovermode='x unified',
                    height=500
                )
                
                st.plotly_chart(fig_vl, use_container_width=True)
                
                # Statistiques descriptives
                st.markdown("---")
                st.subheader("Statistiques Descriptives par FCP")
                
                stats_list = []
                for fcp in df_filtered['FCP'].unique():
                    df_fcp = df_filtered[df_filtered['FCP'] == fcp]
                    stats_list.append({
                        'FCP': fcp,
                        'VL Actuelle': df_fcp['VL'].iloc[-1],
                        'VL Minimale': df_fcp['VL'].min(),
                        'VL Maximale': df_fcp['VL'].max(),
                        'VL Moyenne': df_fcp['VL'].mean(),
                        'Écart-Type': df_fcp['VL'].std()
                    })
                
                df_stats = pd.DataFrame(stats_list)
                
                # Formater pour l'affichage
                df_stats_display = df_stats.copy()
                for col in ['VL Actuelle', 'VL Minimale', 'VL Maximale', 'VL Moyenne', 'Écart-Type']:
                    df_stats_display[col] = df_stats_display[col].apply(lambda x: f"{x:,.2f} FCFA")
                
                st.dataframe(df_stats_display, use_container_width=True, hide_index=True)
            
            # --- TAB 2: PERFORMANCE ---
            with tab2:
                st.subheader("Analyse de Performance")
                
                # Calculer les rendements
                performance_list = []
                
                for fcp in df_filtered['FCP'].unique():
                    df_fcp = df_filtered[df_filtered['FCP'] == fcp].sort_values('Date')
                    
                    if len(df_fcp) >= 2:
                        vl_first = df_fcp['VL'].iloc[0]
                        vl_last = df_fcp['VL'].iloc[-1]
                        
                        # Rendement total
                        rendement_total = ((vl_last - vl_first) / vl_first) * 100
                        
                        # Calculer les rendements quotidiens
                        df_fcp['Rendement'] = df_fcp['VL'].pct_change() * 100
                        rendement_moyen = df_fcp['Rendement'].mean()
                        volatilite = df_fcp['Rendement'].std()
                        
                        # Ratio de Sharpe simplifié (rendement / volatilité)
                        sharpe = rendement_moyen / volatilite if volatilite != 0 else 0
                        
                        performance_list.append({
                            'FCP': fcp,
                            'Rendement Total (%)': rendement_total,
                            'Rendement Moyen (%)': rendement_moyen,
                            'Volatilité (%)': volatilite,
                            'Ratio Sharpe': sharpe
                        })
                
                df_perf = pd.DataFrame(performance_list)
                df_perf = df_perf.sort_values('Rendement Total (%)', ascending=False)
                
                # Graphique de performance
                fig_perf = go.Figure()
                
                fig_perf.add_trace(go.Bar(
                    x=df_perf['FCP'],
                    y=df_perf['Rendement Total (%)'],
                    marker_color=df_perf['Rendement Total (%)'].apply(
                        lambda x: 'green' if x > 0 else 'red'
                    ),
                    text=df_perf['Rendement Total (%)'].apply(lambda x: f"{x:.2f}%"),
                    textposition='outside'
                ))
                
                fig_perf.update_layout(
                    title='Rendement Total par FCP',
                    xaxis_title='FCP',
                    yaxis_title='Rendement Total (%)',
                    height=400
                )
                
                st.plotly_chart(fig_perf, use_container_width=True)
                
                # Tableau de performance
                st.markdown("---")
                st.subheader("Tableau de Performance Détaillé")
                
                df_perf_display = df_perf.copy()
                for col in ['Rendement Total (%)', 'Rendement Moyen (%)', 'Volatilité (%)']:
                    df_perf_display[col] = df_perf_display[col].apply(lambda x: f"{x:.4f}%")
                df_perf_display['Ratio Sharpe'] = df_perf_display['Ratio Sharpe'].apply(lambda x: f"{x:.4f}")
                
                st.dataframe(df_perf_display, use_container_width=True, hide_index=True)
                
                # Graphique Rendement vs Risque
                st.markdown("---")
                st.subheader("Graphique Rendement-Risque")
                
                fig_risk = go.Figure()
                
                fig_risk.add_trace(go.Scatter(
                    x=df_perf['Volatilité (%)'],
                    y=df_perf['Rendement Total (%)'],
                    mode='markers+text',
                    text=df_perf['FCP'],
                    textposition='top center',
                    marker=dict(
                        size=15,
                        color=df_perf['Ratio Sharpe'],
                        colorscale='RdYlGn',
                        showscale=True,
                        colorbar=dict(title="Ratio Sharpe")
                    )
                ))
                
                fig_risk.update_layout(
                    title='Relation Rendement-Risque (Volatilité)',
                    xaxis_title='Volatilité (%)',
                    yaxis_title='Rendement Total (%)',
                    height=500
                )
                
                st.plotly_chart(fig_risk, use_container_width=True)
            
            # --- TAB 3: ANALYSE DE RISQUE ---
            with tab3:
                st.subheader("Analyse de Risque")
                
                # Calculer les drawdowns
                risk_analysis = []
                
                for fcp in df_filtered['FCP'].unique():
                    df_fcp = df_filtered[df_filtered['FCP'] == fcp].sort_values('Date')
                    
                    if len(df_fcp) >= 2:
                        # Calculer le drawdown
                        df_fcp['Max_VL'] = df_fcp['VL'].cummax()
                        df_fcp['Drawdown'] = ((df_fcp['VL'] - df_fcp['Max_VL']) / df_fcp['Max_VL']) * 100
                        
                        max_drawdown = df_fcp['Drawdown'].min()
                        
                        # Value at Risk (VaR) 95%
                        df_fcp['Rendement'] = df_fcp['VL'].pct_change() * 100
                        var_95 = df_fcp['Rendement'].quantile(0.05)
                        
                        risk_analysis.append({
                            'FCP': fcp,
                            'Drawdown Maximum (%)': max_drawdown,
                            'VaR 95% (%)': var_95
                        })
                
                df_risk = pd.DataFrame(risk_analysis)
                
                # Graphique de drawdown
                if len(selected_fcps) == 1:
                    # Afficher le drawdown pour un FCP unique
                    fcp = selected_fcps[0]
                    df_fcp = df_filtered[df_filtered['FCP'] == fcp].sort_values('Date')
                    df_fcp['Max_VL'] = df_fcp['VL'].cummax()
                    df_fcp['Drawdown'] = ((df_fcp['VL'] - df_fcp['Max_VL']) / df_fcp['Max_VL']) * 100
                    
                    fig_dd = go.Figure()
                    
                    fig_dd.add_trace(go.Scatter(
                        x=df_fcp['Date'],
                        y=df_fcp['Drawdown'],
                        name='Drawdown',
                        mode='lines',
                        fill='tozeroy',
                        fillcolor='rgba(255, 0, 0, 0.2)',
                        line=dict(color='red', width=2)
                    ))
                    
                    fig_dd.update_layout(
                        title=f'Évolution du Drawdown - {fcp}',
                        xaxis_title='Date',
                        yaxis_title='Drawdown (%)',
                        height=400
                    )
                    
                    st.plotly_chart(fig_dd, use_container_width=True)
                
                # Tableau d'analyse de risque
                st.markdown("---")
                st.subheader("Métriques de Risque")
                
                df_risk_display = df_risk.copy()
                df_risk_display['Drawdown Maximum (%)'] = df_risk_display['Drawdown Maximum (%)'].apply(lambda x: f"{x:.2f}%")
                df_risk_display['VaR 95% (%)'] = df_risk_display['VaR 95% (%)'].apply(lambda x: f"{x:.2f}%")
                
                st.dataframe(df_risk_display, use_container_width=True, hide_index=True)
                
                # Graphique comparatif
                if len(df_risk) > 1:
                    fig_risk_comp = go.Figure()
                    
                    fig_risk_comp.add_trace(go.Bar(
                        x=df_risk['FCP'],
                        y=df_risk['Drawdown Maximum (%)'],
                        name='Drawdown Max',
                        marker_color='red'
                    ))
                    
                    fig_risk_comp.update_layout(
                        title='Comparaison du Drawdown Maximum',
                        xaxis_title='FCP',
                        yaxis_title='Drawdown (%)',
                        height=400
                    )
                    
                    st.plotly_chart(fig_risk_comp, use_container_width=True)
            
            # --- TAB 4: DONNÉES DÉTAILLÉES ---
            with tab4:
                st.subheader("Données Brutes")
                
                # Options de filtrage
                col1, col2 = st.columns(2)
                
                with col1:
                    date_min = df_filtered['Date'].min()
                    date_max = df_filtered['Date'].max()
                    
                    start_date = st.date_input(
                        "Date de début",
                        value=date_min,
                        min_value=date_min,
                        max_value=date_max
                    )
                
                with col2:
                    end_date = st.date_input(
                        "Date de fin",
                        value=date_max,
                        min_value=date_min,
                        max_value=date_max
                    )
                
                # Filtrer par période
                df_period = df_filtered[
                    (df_filtered['Date'] >= pd.Timestamp(start_date)) &
                    (df_filtered['Date'] <= pd.Timestamp(end_date))
                ].copy()
                
                # Formater pour l'affichage
                df_display = df_period.copy()
                df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
                df_display['VL'] = df_display['VL'].apply(lambda x: f"{x:,.2f} FCFA")
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Bouton de téléchargement
                csv = df_period.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Télécharger les données en CSV",
                    data=csv,
                    file_name=f"vl_{filter_text.replace(', ', '_')}_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )
        
        else:
            st.error("Le fichier doit contenir les colonnes: FCP, Date, VL")
    
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier: {str(e)}")
        st.exception(e)

else:
    st.info("👆 Veuillez charger un fichier Excel contenant les données de Valeurs Liquidatives")
    
    st.markdown("""
    <div class="info-box">
        <h4>📋 Format du fichier attendu</h4>
        <p>Le fichier Excel doit contenir les colonnes suivantes :</p>
        <ul>
            <li><strong>FCP</strong> : Nom du fonds commun de placement</li>
            <li><strong>Date</strong> : Date de la valeur liquidative (format date)</li>
            <li><strong>VL</strong> : Valeur liquidative en FCFA</li>
        </ul>
        <p><strong>Note :</strong> Si aucun FCP n'est sélectionné dans le filtre, tous les FCP seront analysés par défaut.</p>
    </div>
    """, unsafe_allow_html=True)

# Pied de page
st.markdown("---")
st.caption("**Gestion Obligataire** - Module d'Analyse des Valeurs Liquidatives | Toutes les valeurs en FCFA")
