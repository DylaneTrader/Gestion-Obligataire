"""
Page d'analyse des souscriptions et rachats
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

st.title("📊 Souscriptions et Rachats")
st.markdown("### Analyse des flux de souscriptions et rachats des FCP")

# Onglets principaux
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Concentration des Flux",
    "📉 Volatilité et Stabilité",
    "🌡️ Saisonnalité Approfondie",
    "📊 Analyse par Type de Client et Heatmap - Tous les FCP"
])

# --- TAB 1: CONCENTRATION DES FLUX ---
with tab1:
    st.header("Concentration des Flux Nets")
    
    # Section pour charger les données
    st.subheader("Chargement des données")
    uploaded_file = st.file_uploader(
        "Charger un fichier Excel avec les données de flux",
        type=['xlsx', 'xls'],
        key="flux_file"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            
            # Vérifier si les colonnes nécessaires existent
            required_cols = ['FCP', 'Date', 'Flux_Net']
            if all(col in df.columns for col in required_cols):
                # Obtenir la dernière date
                df['Date'] = pd.to_datetime(df['Date'])
                last_date = df['Date'].max()
                
                # Calculer la concentration des flux
                flux_by_fcp = df.groupby('FCP')['Flux_Net'].sum().reset_index()
                flux_by_fcp = flux_by_fcp.sort_values('Flux_Net', ascending=False)
                
                # Calculer la part cumulative
                total_flux = flux_by_fcp['Flux_Net'].abs().sum()
                flux_by_fcp['Part'] = (flux_by_fcp['Flux_Net'].abs() / total_flux * 100)
                flux_by_fcp['Part_Cumulative'] = flux_by_fcp['Part'].cumsum()
                
                # Calculer la part à la dernière date
                last_date_data = df[df['Date'] == last_date].groupby('FCP')['Flux_Net'].sum().reset_index()
                last_date_data.columns = ['FCP', 'Flux_Derniere_Date']
                total_last_date = last_date_data['Flux_Derniere_Date'].abs().sum()
                last_date_data[f'Part au {last_date.strftime("%Y-%m-%d")}'] = (
                    last_date_data['Flux_Derniere_Date'].abs() / total_last_date * 100
                )
                
                # Fusionner les données
                flux_by_fcp = flux_by_fcp.merge(
                    last_date_data[['FCP', f'Part au {last_date.strftime("%Y-%m-%d")}']],
                    on='FCP',
                    how='left'
                )
                
                # Formater pour l'affichage
                display_df = flux_by_fcp.copy()
                display_df['Flux_Net'] = display_df['Flux_Net'].apply(lambda x: f"{x:,.2f} FCFA")
                display_df['Part'] = display_df['Part'].apply(lambda x: f"{x:.2f}%")
                display_df['Part_Cumulative'] = display_df['Part_Cumulative'].apply(lambda x: f"{x:.2f}%")
                display_df[f'Part au {last_date.strftime("%Y-%m-%d")}'] = display_df[f'Part au {last_date.strftime("%Y-%m-%d")}'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
                
                st.subheader("Tableau de Concentration des Flux Nets")
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # Diagramme de Pareto
                st.subheader("Diagramme de Pareto - Concentration des Flux")
                
                fig = go.Figure()
                
                # Barres pour les flux
                fig.add_trace(go.Bar(
                    x=flux_by_fcp['FCP'],
                    y=flux_by_fcp['Flux_Net'].abs(),
                    name='Flux Net (valeur absolue)',
                    yaxis='y',
                    marker_color='steelblue'
                ))
                
                # Ligne pour la part cumulative
                fig.add_trace(go.Scatter(
                    x=flux_by_fcp['FCP'],
                    y=flux_by_fcp['Part_Cumulative'],
                    name='Part Cumulative',
                    yaxis='y2',
                    mode='lines+markers',
                    line=dict(color='red', width=2),
                    marker=dict(size=8)
                ))
                
                # Ligne de référence 80%
                fig.add_hline(
                    y=80, 
                    line_dash="dash", 
                    line_color="green",
                    annotation_text="80%",
                    yref='y2'
                )
                
                fig.update_layout(
                    title='Diagramme de Pareto - Concentration des Flux Nets par FCP',
                    xaxis_title='FCP',
                    yaxis=dict(
                        title='Flux Net (FCFA)',
                        side='left'
                    ),
                    yaxis2=dict(
                        title='Part Cumulative (%)',
                        side='right',
                        overlaying='y',
                        range=[0, 100]
                    ),
                    hovermode='x unified',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Note d'interprétation
                st.markdown("""
                <div class="info-box">
                    <h4>📝 Note d'Interprétation du Diagramme de Pareto</h4>
                    <p><strong>Principe 80/20 :</strong> Le diagramme de Pareto permet d'identifier les FCP qui représentent 
                    la majorité des flux nets. Généralement, environ 20% des FCP génèrent 80% des flux totaux.</p>
                    
                    <p><strong>Analyse de la concentration :</strong></p>
                    <ul>
                        <li><strong>Forte concentration</strong> : Si la ligne rouge atteint 80% rapidement (avec peu de FCP), 
                        cela indique que les flux sont concentrés sur quelques FCP majeurs.</li>
                        <li><strong>Faible concentration</strong> : Si la ligne monte progressivement, les flux sont 
                        répartis plus uniformément entre les FCP.</li>
                    </ul>
                    
                    <p><strong>Implications :</strong></p>
                    <ul>
                        <li>Une forte concentration peut indiquer des risques de liquidité si les principaux FCP 
                        subissent des rachats massifs.</li>
                        <li>Permet d'identifier les FCP stratégiques nécessitant une surveillance prioritaire.</li>
                        <li>Guide les décisions d'allocation de ressources et de gestion du risque.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.warning("Le fichier doit contenir les colonnes: FCP, Date, Flux_Net")
                
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier: {str(e)}")
    else:
        st.info("👆 Veuillez charger un fichier Excel avec les données de flux pour afficher l'analyse")

# --- TAB 2: VOLATILITÉ ET STABILITÉ ---
with tab2:
    st.header("Volatilité et Stabilité des Flux")
    
    # Filtre FCP
    st.subheader("Filtres")
    
    uploaded_file_vol = st.file_uploader(
        "Charger un fichier Excel avec les données de flux (si différent)",
        type=['xlsx', 'xls'],
        key="volatility_file"
    )
    
    if uploaded_file_vol is not None or uploaded_file is not None:
        try:
            # Utiliser le fichier chargé dans cet onglet ou le précédent
            file_to_use = uploaded_file_vol if uploaded_file_vol is not None else uploaded_file
            df_vol = pd.read_excel(file_to_use)
            
            if all(col in df_vol.columns for col in ['FCP', 'Date', 'Flux_Net']):
                df_vol['Date'] = pd.to_datetime(df_vol['Date'])
                
                # Liste des FCP
                fcp_list = ['Tous les FCP'] + sorted(df_vol['FCP'].unique().tolist())
                
                selected_fcp = st.selectbox(
                    "Sélectionner un FCP",
                    options=fcp_list,
                    help="Sélectionnez un FCP spécifique ou 'Tous les FCP' pour une analyse globale"
                )
                
                # Filtrer les données selon la sélection
                if selected_fcp != 'Tous les FCP':
                    df_analysis = df_vol[df_vol['FCP'] == selected_fcp].copy()
                else:
                    df_analysis = df_vol.copy()
                
                # Analyser par période
                df_analysis = df_analysis.sort_values('Date')
                df_analysis['Flux_Abs'] = df_analysis['Flux_Net'].abs()
                
                # Calculer des métriques de volatilité
                st.markdown("---")
                st.subheader("Analyse de Volatilité Améliorée")
                
                # Grouper par date pour avoir une série temporelle
                if selected_fcp != 'Tous les FCP':
                    time_series = df_analysis.groupby('Date')['Flux_Net'].sum().reset_index()
                else:
                    time_series = df_analysis.groupby(['Date', 'FCP'])['Flux_Net'].sum().reset_index()
                    time_series = time_series.groupby('Date')['Flux_Net'].sum().reset_index()
                
                # Calculer l'écart-type mobile et la moyenne mobile
                time_series['MA_4w'] = time_series['Flux_Net'].rolling(window=4, min_periods=1).mean()
                time_series['Std_4w'] = time_series['Flux_Net'].rolling(window=4, min_periods=1).std()
                time_series['CV_4w'] = (time_series['Std_4w'] / time_series['MA_4w'].abs()) * 100
                
                # Calculer les bandes de Bollinger
                # Les bandes de Bollinger offrent une meilleure visualisation de la volatilité que le CV mobile
                # car elles montrent la dispersion autour de la tendance et permettent d'identifier les valeurs extrêmes
                time_series['Upper_Band'] = time_series['MA_4w'] + (2 * time_series['Std_4w'])
                time_series['Lower_Band'] = time_series['MA_4w'] - (2 * time_series['Std_4w'])
                
                # Graphique de volatilité avec bandes de Bollinger
                fig_vol = go.Figure()
                
                # Flux nets
                fig_vol.add_trace(go.Scatter(
                    x=time_series['Date'],
                    y=time_series['Flux_Net'],
                    name='Flux Net',
                    mode='lines+markers',
                    line=dict(color='steelblue', width=2)
                ))
                
                # Moyenne mobile
                fig_vol.add_trace(go.Scatter(
                    x=time_series['Date'],
                    y=time_series['MA_4w'],
                    name='Moyenne Mobile (4 sem)',
                    mode='lines',
                    line=dict(color='orange', width=2, dash='dash')
                ))
                
                # Bandes de Bollinger
                fig_vol.add_trace(go.Scatter(
                    x=time_series['Date'],
                    y=time_series['Upper_Band'],
                    name='Bande Supérieure',
                    mode='lines',
                    line=dict(color='red', width=1, dash='dot'),
                    showlegend=True
                ))
                
                fig_vol.add_trace(go.Scatter(
                    x=time_series['Date'],
                    y=time_series['Lower_Band'],
                    name='Bande Inférieure',
                    mode='lines',
                    line=dict(color='red', width=1, dash='dot'),
                    fill='tonexty',
                    fillcolor='rgba(255, 0, 0, 0.1)',
                    showlegend=True
                ))
                
                title_text = f'Analyse de Volatilité avec Bandes de Bollinger - {selected_fcp}'
                fig_vol.update_layout(
                    title=title_text,
                    xaxis_title='Date',
                    yaxis_title='Flux Net (FCFA)',
                    hovermode='x unified',
                    height=500
                )
                
                st.plotly_chart(fig_vol, use_container_width=True)
                
                # Métriques de volatilité
                st.markdown("---")
                st.subheader("Métriques de Volatilité")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    mean_flux = time_series['Flux_Net'].mean()
                    st.metric("Flux Moyen", f"{mean_flux:,.2f} FCFA")
                
                with col2:
                    std_flux = time_series['Flux_Net'].std()
                    st.metric("Écart-Type", f"{std_flux:,.2f} FCFA")
                
                with col3:
                    cv = (std_flux / abs(mean_flux)) * 100 if mean_flux != 0 else 0
                    st.metric("Coefficient de Variation", f"{cv:.2f}%")
                
                with col4:
                    volatility_score = "Faible" if cv < 50 else "Moyenne" if cv < 100 else "Élevée"
                    st.metric("Niveau de Volatilité", volatility_score)
                
            else:
                st.warning("Le fichier doit contenir les colonnes: FCP, Date, Flux_Net")
                
        except Exception as e:
            st.error(f"Erreur lors de l'analyse: {str(e)}")
    else:
        st.info("👆 Veuillez charger un fichier Excel pour afficher l'analyse de volatilité")

# --- TAB 3: SAISONNALITÉ APPROFONDIE ---
with tab3:
    st.header("Saisonnalité Approfondie")
    
    # Filtres
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file_seas = st.file_uploader(
            "Charger un fichier Excel avec les données",
            type=['xlsx', 'xls'],
            key="seasonality_file"
        )
    
    if uploaded_file_seas is not None or uploaded_file is not None:
        try:
            file_to_use = uploaded_file_seas if uploaded_file_seas is not None else uploaded_file
            df_seas = pd.read_excel(file_to_use)
            
            if all(col in df_seas.columns for col in ['FCP', 'Date', 'Souscriptions', 'Rachats']):
                df_seas['Date'] = pd.to_datetime(df_seas['Date'])
                df_seas['Flux_Net'] = df_seas['Souscriptions'] - df_seas['Rachats']
                
                # Filtres
                with col2:
                    fcp_list_seas = ['Tous les FCP'] + sorted(df_seas['FCP'].unique().tolist())
                    selected_fcp_seas = st.selectbox(
                        "Sélectionner un FCP",
                        options=fcp_list_seas,
                        key="fcp_seasonality"
                    )
                
                metric_choice = st.radio(
                    "Métrique à analyser",
                    options=['Souscriptions', 'Rachats', 'Flux_Net'],
                    horizontal=True,
                    format_func=lambda x: {'Souscriptions': 'Souscriptions', 'Rachats': 'Rachats', 'Flux_Net': 'Flux Nets'}[x]
                )
                
                # Filtrer selon FCP
                if selected_fcp_seas != 'Tous les FCP':
                    df_analysis_seas = df_seas[df_seas['FCP'] == selected_fcp_seas].copy()
                else:
                    df_analysis_seas = df_seas.copy()
                
                # Extraire les composantes temporelles
                df_analysis_seas['Mois'] = df_analysis_seas['Date'].dt.month
                df_analysis_seas['Trimestre'] = df_analysis_seas['Date'].dt.quarter
                df_analysis_seas['Annee'] = df_analysis_seas['Date'].dt.year
                
                # Analyse par mois
                monthly_data = df_analysis_seas.groupby('Mois')[metric_choice].sum().reset_index()
                monthly_data['Mois_Nom'] = monthly_data['Mois'].apply(
                    lambda x: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                              'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'][x-1]
                )
                
                # Graphique de saisonnalité
                fig_seas = go.Figure()
                
                fig_seas.add_trace(go.Bar(
                    x=monthly_data['Mois_Nom'],
                    y=monthly_data[metric_choice],
                    marker_color='teal',
                    text=monthly_data[metric_choice].apply(lambda x: f"{x:,.0f}"),
                    textposition='outside'
                ))
                
                fig_seas.update_layout(
                    title=f'Saisonnalité Mensuelle - {metric_choice}',
                    xaxis_title='Mois',
                    yaxis_title=f'{metric_choice} (FCFA)',
                    height=400
                )
                
                st.plotly_chart(fig_seas, use_container_width=True)
                
                # Heatmap par année et mois
                st.markdown("---")
                st.subheader("Heatmap Année-Mois")
                
                heatmap_data = df_analysis_seas.groupby(['Annee', 'Mois'])[metric_choice].sum().reset_index()
                heatmap_pivot = heatmap_data.pivot(index='Annee', columns='Mois', values=metric_choice)
                
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=heatmap_pivot.values,
                    x=['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'],
                    y=heatmap_pivot.index,
                    colorscale='RdYlGn',
                    text=heatmap_pivot.values,
                    texttemplate='%{text:,.0f}',
                    textfont={"size": 10}
                ))
                
                fig_heatmap.update_layout(
                    title=f'Heatmap {metric_choice} par Année et Mois',
                    xaxis_title='Mois',
                    yaxis_title='Année',
                    height=400
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Carte d'interprétation
                st.markdown("---")
                
                # Calculer les statistiques pour l'interprétation
                mean_value = monthly_data[metric_choice].mean()
                max_month = monthly_data.loc[monthly_data[metric_choice].idxmax(), 'Mois_Nom']
                min_month = monthly_data.loc[monthly_data[metric_choice].idxmin(), 'Mois_Nom']
                max_value = monthly_data[metric_choice].max()
                min_value = monthly_data[metric_choice].min()
                # Protection contre division par zéro et valeurs très petites
                if abs(mean_value) > 0.01:
                    variation = ((max_value - min_value) / abs(mean_value) * 100)
                else:
                    variation = 0
                
                metric_name = {'Souscriptions': 'des souscriptions', 'Rachats': 'des rachats', 'Flux_Net': 'des flux nets'}[metric_choice]
                fcp_text = selected_fcp_seas if selected_fcp_seas != 'Tous les FCP' else 'tous les FCP'
                
                st.markdown(f"""
                <div class="success-box">
                    <h4>📊 Carte d'Interprétation - Saisonnalité {metric_name}</h4>
                    <p><strong>FCP analysé :</strong> {fcp_text}</p>
                    
                    <p><strong>Tendances observées :</strong></p>
                    <ul>
                        <li><strong>Mois le plus actif :</strong> {max_month} avec {max_value:,.2f} FCFA</li>
                        <li><strong>Mois le moins actif :</strong> {min_month} avec {min_value:,.2f} FCFA</li>
                        <li><strong>Moyenne mensuelle :</strong> {mean_value:,.2f} FCFA</li>
                        <li><strong>Amplitude de variation :</strong> {variation:.1f}%</li>
                    </ul>
                    
                    <p><strong>Analyse :</strong></p>
                    <ul>
                        <li>{"Une forte saisonnalité est observée" if variation > 50 else "La saisonnalité est modérée" if variation > 20 else "Peu de saisonnalité détectée"}</li>
                        <li>Les périodes de forte activité peuvent nécessiter une gestion de liquidité renforcée</li>
                        <li>Les tendances historiques peuvent guider les prévisions et la planification</li>
                    </ul>
                    
                    <p><strong>Recommandations :</strong></p>
                    <ul>
                        <li>Anticiper les besoins de liquidité durant les mois de forte activité</li>
                        <li>Adapter les stratégies commerciales en fonction des cycles saisonniers</li>
                        <li>Surveiller les écarts par rapport aux patterns historiques</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.warning("Le fichier doit contenir les colonnes: FCP, Date, Souscriptions, Rachats")
                
        except Exception as e:
            st.error(f"Erreur lors de l'analyse: {str(e)}")
    else:
        st.info("👆 Veuillez charger un fichier Excel pour afficher l'analyse de saisonnalité")

# --- TAB 4: ANALYSE PAR TYPE DE CLIENT ET HEATMAP ---
with tab4:
    st.header("Analyse par Type de Client et Heatmap - Tous les FCP")
    
    # Sous-onglets
    subtab1, subtab2 = st.tabs(["📊 Analyse par Type de Client", "👥 Dynamique Client"])
    
    with subtab1:
        st.subheader("Répartition par Type de Client")
        
        uploaded_file_client = st.file_uploader(
            "Charger un fichier Excel avec les données clients",
            type=['xlsx', 'xls'],
            key="client_file"
        )
        
        if uploaded_file_client is not None:
            try:
                df_client = pd.read_excel(uploaded_file_client)
                
                if all(col in df_client.columns for col in ['Type_Client', 'FCP', 'Montant']):
                    # Analyse par type de client
                    client_analysis = df_client.groupby('Type_Client')['Montant'].sum().reset_index()
                    client_analysis = client_analysis.sort_values('Montant', ascending=False)
                    
                    # Graphique en camembert
                    fig_client = go.Figure(data=[go.Pie(
                        labels=client_analysis['Type_Client'],
                        values=client_analysis['Montant'],
                        hole=0.4
                    )])
                    
                    fig_client.update_layout(
                        title='Répartition par Type de Client',
                        height=400
                    )
                    
                    st.plotly_chart(fig_client, use_container_width=True)
                    
                    # Tableau détaillé
                    st.markdown("---")
                    display_client = client_analysis.copy()
                    display_client['Montant'] = display_client['Montant'].apply(lambda x: f"{x:,.2f} FCFA")
                    display_client['Part'] = (client_analysis['Montant'] / client_analysis['Montant'].sum() * 100).apply(lambda x: f"{x:.2f}%")
                    
                    st.dataframe(display_client, use_container_width=True, hide_index=True)
                    
                    # Heatmap Type Client x FCP
                    st.markdown("---")
                    st.subheader("Heatmap Type de Client x FCP")
                    
                    heatmap_client_fcp = df_client.groupby(['Type_Client', 'FCP'])['Montant'].sum().reset_index()
                    heatmap_pivot_client = heatmap_client_fcp.pivot(index='Type_Client', columns='FCP', values='Montant')
                    
                    fig_heatmap_client = go.Figure(data=go.Heatmap(
                        z=heatmap_pivot_client.values,
                        x=heatmap_pivot_client.columns,
                        y=heatmap_pivot_client.index,
                        colorscale='Blues',
                        text=heatmap_pivot_client.values,
                        texttemplate='%{text:,.0f}',
                        textfont={"size": 9}
                    ))
                    
                    fig_heatmap_client.update_layout(
                        title='Distribution des Montants par Type de Client et FCP',
                        xaxis_title='FCP',
                        yaxis_title='Type de Client',
                        height=500
                    )
                    
                    st.plotly_chart(fig_heatmap_client, use_container_width=True)
                    
                else:
                    st.warning("Le fichier doit contenir les colonnes: Type_Client, FCP, Montant")
                    
            except Exception as e:
                st.error(f"Erreur lors de l'analyse: {str(e)}")
        else:
            st.info("👆 Veuillez charger un fichier Excel pour afficher l'analyse par type de client")
    
    with subtab2:
        st.subheader("Dynamique Client")
        st.markdown("*Section déplacée depuis Analyses Avancées*")
        
        uploaded_file_dynamic = st.file_uploader(
            "Charger un fichier Excel avec les données de dynamique client",
            type=['xlsx', 'xls'],
            key="dynamic_file"
        )
        
        if uploaded_file_dynamic is not None:
            try:
                df_dynamic = pd.read_excel(uploaded_file_dynamic)
                
                if all(col in df_dynamic.columns for col in ['Date', 'Nouveaux_Clients', 'Clients_Sortants', 'Clients_Actifs']):
                    df_dynamic['Date'] = pd.to_datetime(df_dynamic['Date'])
                    df_dynamic = df_dynamic.sort_values('Date')
                    
                    # Graphique d'évolution
                    fig_dynamic = go.Figure()
                    
                    fig_dynamic.add_trace(go.Scatter(
                        x=df_dynamic['Date'],
                        y=df_dynamic['Nouveaux_Clients'],
                        name='Nouveaux Clients',
                        mode='lines+markers',
                        line=dict(color='green', width=2)
                    ))
                    
                    fig_dynamic.add_trace(go.Scatter(
                        x=df_dynamic['Date'],
                        y=df_dynamic['Clients_Sortants'],
                        name='Clients Sortants',
                        mode='lines+markers',
                        line=dict(color='red', width=2)
                    ))
                    
                    fig_dynamic.add_trace(go.Scatter(
                        x=df_dynamic['Date'],
                        y=df_dynamic['Clients_Actifs'],
                        name='Clients Actifs',
                        mode='lines+markers',
                        line=dict(color='blue', width=2),
                        yaxis='y2'
                    ))
                    
                    fig_dynamic.update_layout(
                        title='Dynamique Client',
                        xaxis_title='Date',
                        yaxis=dict(title='Nouveaux/Sortants'),
                        yaxis2=dict(
                            title='Clients Actifs',
                            overlaying='y',
                            side='right'
                        ),
                        hovermode='x unified',
                        height=500
                    )
                    
                    st.plotly_chart(fig_dynamic, use_container_width=True)
                    
                    # Métriques
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_new = df_dynamic['Nouveaux_Clients'].sum()
                        st.metric("Total Nouveaux Clients", f"{total_new:,.0f}")
                    
                    with col2:
                        total_out = df_dynamic['Clients_Sortants'].sum()
                        st.metric("Total Clients Sortants", f"{total_out:,.0f}")
                    
                    with col3:
                        net_change = total_new - total_out
                        st.metric("Variation Nette", f"{net_change:,.0f}")
                    
                    with col4:
                        current_active = df_dynamic['Clients_Actifs'].iloc[-1]
                        st.metric("Clients Actifs Actuels", f"{current_active:,.0f}")
                    
                else:
                    st.warning("Le fichier doit contenir les colonnes: Date, Nouveaux_Clients, Clients_Sortants, Clients_Actifs")
                    
            except Exception as e:
                st.error(f"Erreur lors de l'analyse: {str(e)}")
        else:
            st.info("👆 Veuillez charger un fichier Excel pour afficher la dynamique client")

# Pied de page
st.markdown("---")
st.caption("**Gestion Obligataire** - Module d'Analyse des Souscriptions et Rachats | Toutes les valeurs en FCFA")
