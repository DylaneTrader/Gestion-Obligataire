# 📊 Gestion Obligataire

Application Streamlit avancée pour l'analyse, le pricing et la gestion de portefeuilles d'obligations.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red)

## 📖 Description

**Gestion Obligataire** est une application professionnelle qui combine des modèles mathématiques rigoureux avec une interface utilisateur intuitive pour faciliter l'analyse et la gestion d'obligations. Elle s'adresse aux investisseurs, analystes financiers et gestionnaires de portefeuille.

## 🎯 Fonctionnalités Principales

### 📈 Pricing d'Obligations
- **Calcul de prix théorique** : Prix d'obligations basé sur les paramètres fondamentaux
- **Rendement à l'échéance (YTM)** : Calcul par méthode itérative de Newton-Raphson
- **Rendement courant** : Analyse du rendement instantané
- **Analyse de sensibilité** : Impact des variations de rendement sur le prix
- **Courbes de prix** : Visualisations interactives (prix vs rendement, maturité, coupon)
- **Flux de trésorerie** : Calendrier complet des paiements avec actualisation

### 📊 Métriques de Risque
- **Duration de Macaulay** : Durée de vie moyenne pondérée des flux
- **Duration modifiée** : Sensibilité du prix aux variations de taux
- **Convexité** : Courbure de la relation prix-rendement
- **Intérêts courus** : Calcul des coupons courus entre deux dates
- **Valeur actuelle** : Actualisation des flux de trésorerie futurs

### 💼 Gestion de Portefeuille
- **Suivi des positions** : Gestion complète des obligations détenues
- **Calcul P&L** : Profits et pertes réalisés et non réalisés
- **Allocation d'actifs** : Répartition par type d'obligation et notation de crédit
- **Profil de maturité** : Analyse de l'échéancier du portefeuille
- **Métriques agrégées** : Duration et coupon moyens pondérés

### 📉 Visualisations
- **Graphiques interactifs** : Utilisation de Plotly pour des visualisations dynamiques
- **Tableaux de bord** : Métriques en temps réel
- **Analyse comparative** : Comparaison de différents scénarios
- **Exports de données** : Résultats exportables en CSV

## 🏗️ Structure du Projet

```
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
```

## 🚀 Installation et Utilisation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation

1. Clonez le repository :
```bash
git clone https://github.com/DylaneTrader/Gestion-Obligataire.git
cd Gestion-Obligataire
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

### Lancement de l'application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut à l'adresse `http://localhost:8501`.

## 📚 Guide d'Utilisation

### Page d'Accueil
- Présentation générale de l'application
- Calculateur rapide pour des estimations immédiates
- Navigation vers les différents modules

### Bond Pricing
- **Onglet "Calcul de Prix"** : Calculez le prix d'une obligation à partir de ses caractéristiques
- **Onglet "Analyse Complète"** : Obtenez toutes les métriques de risque
- **Onglet "Courbe de Prix"** : Visualisez la relation prix-rendement, prix-maturité ou prix-coupon
- **Onglet "Flux de Trésorerie"** : Consultez le calendrier des paiements

### Portfolio Analysis
- **Onglet "Positions"** : Consultez toutes vos positions obligataires
- **Onglet "Analyse"** : Visualisez la répartition et la performance de votre portefeuille
- **Onglet "Ajouter Position"** : Ajoutez de nouvelles obligations à votre portefeuille

### About
- Documentation complète de l'application
- Formules mathématiques utilisées
- Architecture technique
- Guide d'utilisation détaillé

## 📐 Formules Mathématiques

### Prix d'une Obligation
```
P = Σ(C / (1+y)^t) + F / (1+y)^n
```
Où :
- **P** = Prix de l'obligation
- **C** = Paiement du coupon périodique
- **F** = Valeur nominale
- **y** = Rendement périodique
- **n** = Nombre de périodes

### Duration de Macaulay
```
D_Mac = Σ(t × CF_t / (1+y)^t) / P
```

### Duration Modifiée
```
D_Mod = D_Mac / (1 + y)
```

### Convexité
```
C = [Σ(CF_t × t × (t+1) / (1+y)^t)] / [P × (1+y)^2]
```

## 🛠️ Technologies Utilisées

- **Streamlit** : Framework pour l'interface utilisateur
- **Pandas** : Manipulation et analyse de données
- **NumPy** : Calculs numériques
- **Plotly** : Visualisations interactives
- **Python Dataclasses** : Modélisation des données
- **Type Hints** : Typage statique pour plus de robustesse

## 📊 Modules Principaux

### cores/bond_calculations.py
Contient toutes les formules de calcul :
- `calculate_bond_price()` : Calcul du prix d'une obligation
- `calculate_yield_to_maturity()` : Calcul du YTM par Newton-Raphson
- `calculate_macaulay_duration()` : Duration de Macaulay
- `calculate_modified_duration()` : Duration modifiée
- `calculate_convexity()` : Convexité
- `calculate_accrued_interest()` : Intérêts courus
- `generate_cash_flow_schedule()` : Calendrier des flux
- `calculate_current_yield()` : Rendement courant

### cores/data_models.py
Définit les structures de données :
- `Bond` : Représentation d'une obligation
- `BondPosition` : Position sur une obligation
- `Portfolio` : Portefeuille d'obligations
- `BondType` : Énumération des types d'obligations
- `CreditRating` : Notations de crédit

### cores/config.py
Configuration de l'application :
- Paramètres de page Streamlit
- Thème de couleurs
- Paramètres par défaut
- CSS personnalisé
- Fonctions utilitaires

## 💡 Exemples d'Utilisation

### Calculer le prix d'une obligation
```python
from cores.bond_calculations import calculate_bond_price

price = calculate_bond_price(
    face_value=1000,
    coupon_rate=0.05,
    years_to_maturity=5,
    yield_rate=0.05,
    frequency=2
)
print(f"Prix: {price:.2f} €")
```

### Créer une obligation
```python
from cores.data_models import Bond, BondType
from datetime import datetime, timedelta

bond = Bond(
    name="Obligation XYZ",
    isin="FR0000000000",
    face_value=1000.0,
    coupon_rate=0.05,
    issue_date=datetime.now(),
    maturity_date=datetime.now() + timedelta(days=5*365),
    frequency=2,
    bond_type=BondType.CORPORATE
)
```

## ⚠️ Limitations et Avertissements

- Cette application est fournie à des fins **éducatives et d'analyse**
- Les résultats sont basés sur des **modèles théoriques**
- Les prix réels peuvent différer en raison de **facteurs de marché**
- **Consultez toujours un professionnel** pour des décisions d'investissement réelles
- Les calculs supposent des marchés parfaits et ne prennent pas en compte :
  - La liquidité
  - Les coûts de transaction
  - Les considérations fiscales
  - Le risque de crédit détaillé

## 🔄 Roadmap

### Version 1.1 (À venir)
- [ ] Import de données depuis fichiers Excel/CSV
- [ ] Export des analyses en PDF
- [ ] Courbe des taux d'intérêt
- [ ] Analyse de spread de crédit

### Version 1.2 (Planifiée)
- [ ] Obligations à taux variable
- [ ] Obligations convertibles
- [ ] Analyse de scénarios multiples
- [ ] Backtesting de stratégies

## 📞 Support et Contribution

- **Issues** : Signalez les bugs via GitHub Issues
- **Contributions** : Les pull requests sont les bienvenues
- **Questions** : Consultez d'abord la documentation dans l'onglet "About"

## 📝 Changelog

### Version 1.0.0 (2024)
- ✨ Version initiale
- ✅ Calcul de prix et métriques de base
- ✅ Gestion de portefeuille
- ✅ Visualisations interactives
- ✅ Documentation complète

## ⚖️ Licence

© 2024 DylaneTrader - Tous droits réservés

Cette application est développée à des fins éducatives et d'analyse. 
L'utilisation commerciale nécessite une autorisation préalable.

## 👨‍💻 Auteur

**DylaneTrader**

---

**Développé avec ❤️ en Python et Streamlit**
