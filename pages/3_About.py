"""
Page À Propos de l'application
"""

import streamlit as st
from cores.config import PAGE_CONFIG, apply_custom_css, get_app_info

st.set_page_config(**PAGE_CONFIG)
apply_custom_css()

st.title("ℹ️ À Propos")
st.markdown("### Application de Gestion Obligataire")

# Informations sur l'application
app_info = get_app_info()

# Section principale
st.markdown("""
<div class="info-box">
    <h2>📊 Gestion Obligataire</h2>
    <p><strong>Version:</strong> 1.0.0</p>
    <p><strong>Développé par:</strong> DylaneTrader</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Description
st.header("📖 Description")

st.markdown("""
**Gestion Obligataire** est une application Streamlit avancée conçue pour l'analyse, 
le pricing et la gestion de portefeuilles d'obligations. Elle offre des outils professionnels 
pour les investisseurs, analystes financiers et gestionnaires de portefeuille.

L'application combine des modèles mathématiques rigoureux avec une interface utilisateur 
intuitive pour faciliter la prise de décision dans le domaine des obligations.
""")

st.markdown("---")

# Fonctionnalités
st.header("🎯 Fonctionnalités Principales")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Pricing d'Obligations")
    st.markdown("""
    - **Calcul de prix théorique** : Prix d'obligations à partir des paramètres de base
    - **Rendement à l'échéance (YTM)** : Calcul par méthode itérative
    - **Rendement courant** : Analyse du rendement instantané
    - **Analyse de sensibilité** : Impact des variations de rendement
    - **Courbes de prix** : Visualisation interactive
    - **Flux de trésorerie** : Calendrier complet des paiements
    """)
    
    st.subheader("💼 Gestion de Portefeuille")
    st.markdown("""
    - **Suivi des positions** : Gestion complète des obligations détenues
    - **Calcul P&L** : Profits et pertes réalisés et non réalisés
    - **Allocation d'actifs** : Répartition par type et notation
    - **Profil de maturité** : Analyse de l'échéancier
    - **Métriques agrégées** : Duration et coupon moyens pondérés
    """)

with col2:
    st.subheader("📊 Métriques de Risque")
    st.markdown("""
    - **Duration de Macaulay** : Durée de vie moyenne pondérée
    - **Duration modifiée** : Sensibilité au taux d'intérêt
    - **Convexité** : Courbure de la relation prix-rendement
    - **Intérêts courus** : Calcul des coupons courus
    - **Valeur actuelle** : Actualisation des flux futurs
    """)
    
    st.subheader("📉 Visualisations")
    st.markdown("""
    - **Graphiques interactifs** : Courbes de prix et sensibilité
    - **Tableaux de bord** : Métriques en temps réel
    - **Analyse comparative** : Comparaison de scénarios
    - **Exports de données** : Résultats exportables
    """)

st.markdown("---")

# Architecture
st.header("🏗️ Architecture de l'Application")

st.markdown("""
L'application est structurée de manière modulaire pour faciliter la maintenance et l'évolution :
""")

with st.expander("📁 Structure du Projet"):
    st.code("""
    Gestion-Obligataire/
    ├── app.py                      # Application principale (page d'accueil)
    ├── cores/                      # Modules principaux
    │   ├── bond_calculations.py    # Formules et calculs obligataires
    │   ├── data_models.py          # Modèles de données (Bond, Portfolio, etc.)
    │   └── config.py               # Configuration et constantes
    ├── pages/                      # Pages Streamlit
    │   ├── 1_Bond_Pricing.py       # Pricing et analyse d'obligations
    │   ├── 2_Portfolio_Analysis.py # Gestion de portefeuille
    │   └── 3_About.py              # Page À Propos
    ├── requirements.txt            # Dépendances Python
    └── README.md                   # Documentation
    """, language="text")

st.markdown("---")

# Formules mathématiques
st.header("📐 Formules Mathématiques Utilisées")

with st.expander("💰 Prix d'une Obligation"):
    st.markdown("""
    Le prix d'une obligation est la somme actualisée de tous ses flux de trésorerie futurs :
    """)
    
    st.latex(r"""
    P = \sum_{t=1}^{n} \frac{C}{(1+y)^t} + \frac{F}{(1+y)^n}
    """)
    
    st.markdown("""
    Où :
    - **P** = Prix de l'obligation
    - **C** = Paiement du coupon périodique
    - **F** = Valeur nominale (face value)
    - **y** = Rendement périodique
    - **n** = Nombre de périodes jusqu'à l'échéance
    """)

with st.expander("⏱️ Duration de Macaulay"):
    st.markdown("""
    La duration de Macaulay mesure la durée de vie moyenne pondérée d'une obligation :
    """)
    
    st.latex(r"""
    D_{Mac} = \frac{\sum_{t=1}^{n} t \cdot \frac{CF_t}{(1+y)^t}}{P}
    """)
    
    st.markdown("""
    Où :
    - **D_Mac** = Duration de Macaulay
    - **t** = Période
    - **CF_t** = Flux de trésorerie à la période t
    - **y** = Rendement périodique
    - **P** = Prix de l'obligation
    """)

with st.expander("📊 Duration Modifiée"):
    st.markdown("""
    La duration modifiée mesure la sensibilité du prix aux variations de rendement :
    """)
    
    st.latex(r"""
    D_{Mod} = \frac{D_{Mac}}{1 + y}
    """)
    
    st.markdown("""
    Elle permet d'estimer la variation du prix :
    """)
    
    st.latex(r"""
    \Delta P \approx -D_{Mod} \times P \times \Delta y
    """)

with st.expander("🎯 Convexité"):
    st.markdown("""
    La convexité mesure la courbure de la relation prix-rendement :
    """)
    
    st.latex(r"""
    C = \frac{1}{P \times (1+y)^2} \sum_{t=1}^{n} \frac{CF_t \times t \times (t+1)}{(1+y)^t}
    """)
    
    st.markdown("""
    Avec la convexité, l'estimation du prix devient :
    """)
    
    st.latex(r"""
    \Delta P \approx -D_{Mod} \times P \times \Delta y + \frac{1}{2} \times C \times P \times (\Delta y)^2
    """)

st.markdown("---")

# Technologies
st.header("🛠️ Technologies Utilisées")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h4>Frontend</h4>
        <ul>
            <li>Streamlit</li>
            <li>Plotly</li>
            <li>HTML/CSS</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h4>Calculs</h4>
        <ul>
            <li>NumPy</li>
            <li>Pandas</li>
            <li>Python 3.x</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h4>Architecture</h4>
        <ul>
            <li>Dataclasses</li>
            <li>Type Hints</li>
            <li>Design Patterns</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Guide d'utilisation
st.header("📚 Guide d'Utilisation Rapide")

with st.expander("🚀 Démarrage Rapide"):
    st.markdown("""
    1. **Page d'accueil** : Utilisez le calculateur rapide pour des estimations immédiates
    2. **Bond Pricing** : Analysez en détail le pricing et les métriques d'une obligation
    3. **Portfolio Analysis** : Créez et gérez votre portefeuille d'obligations
    4. **Navigation** : Utilisez la barre latérale pour naviguer entre les pages
    """)

with st.expander("💡 Conseils d'Utilisation"):
    st.markdown("""
    - **Paramètres par défaut** : Les valeurs par défaut sont optimisées pour des obligations standard
    - **Visualisations** : Passez la souris sur les graphiques pour plus de détails
    - **Sauvegarde** : Les positions du portefeuille sont sauvegardées dans la session
    - **Exports** : Vous pouvez copier les tableaux pour les exporter
    """)

with st.expander("⚠️ Limitations et Avertissements"):
    st.markdown("""
    - Cette application est fournie à des fins éducatives et d'analyse
    - Les résultats sont basés sur des modèles théoriques
    - Les prix réels peuvent différer en raison de facteurs de marché
    - Consultez toujours un professionnel pour des décisions d'investissement
    """)

st.markdown("---")

# Contact et support
st.header("📞 Contact et Support")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="success-box">
        <h4>💬 Feedback</h4>
        <p>Vos retours sont précieux pour améliorer l'application.</p>
        <p>N'hésitez pas à partager vos suggestions et remarques.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box">
        <h4>🔧 Support Technique</h4>
        <p>Pour toute question technique ou bug :</p>
        <p>Consultez la documentation ou contactez le développeur.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Changelog
st.header("📝 Historique des Versions")

with st.expander("Version 1.0.0 - Initiale"):
    st.markdown("""
    **Fonctionnalités initiales :**
    - Calcul du prix des obligations
    - Calcul du rendement à l'échéance (YTM)
    - Duration de Macaulay et modifiée
    - Convexité
    - Gestion de portefeuille
    - Analyse de sensibilité
    - Visualisations interactives
    - Flux de trésorerie
    """)

st.markdown("---")

# Licence et crédits
st.header("⚖️ Licence et Crédits")

st.markdown("""
<div class="info-box">
    <p><strong>© 2024 DylaneTrader - Gestion Obligataire</strong></p>
    <p>Cette application a été développée avec passion pour faciliter l'analyse obligataire.</p>
    <p>Merci d'utiliser Gestion Obligataire !</p>
</div>
""", unsafe_allow_html=True)

# Pied de page
st.markdown("---")
st.caption("**Gestion Obligataire** v1.0.0 | Développé avec ❤️ par DylaneTrader")
