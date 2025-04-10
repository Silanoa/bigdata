import streamlit as st
import pandas as pd
import snowflake.connector
import os
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import calendar
from datetime import datetime
import numpy as np
import traceback

st.set_page_config(page_title="📊 Dashboard Bookshop", layout="wide", 
                  page_icon="📚", initial_sidebar_state="expanded")

# Application des styles CSS
st.markdown("""
<style>
    .main .block-container {padding-top: 2rem;}
    h1 {color: #1E3A8A;}
    h2 {color: #2563EB;}
    h3 {color: #3B82F6;}
    .metric-card {background-color: #f1f5f9; border-radius: 0.5rem; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.12);}
    .stTabs [data-baseweb="tab-list"] {gap: 2rem;}
    .stTabs [data-baseweb="tab"] {height: 4rem; white-space: pre-wrap;}
</style>
""", unsafe_allow_html=True)

# Fonction de nettoyage des données
def sanitize_dataframe(df, date_columns=None, numeric_columns=None, categorical_columns=None):
    """
    Nettoie un DataFrame en convertissant les colonnes aux types appropriés et en gérant les valeurs invalides.
    
    Args:
        df: DataFrame à nettoyer
        date_columns: Liste des colonnes à convertir en date
        numeric_columns: Liste des colonnes à convertir en nombre
        categorical_columns: Liste des colonnes à convertir en catégorie
    
    Returns:
        DataFrame nettoyé
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Créer une copie pour éviter les problèmes de modification en place
    df_clean = df.copy()
    
    # Convertir les colonnes de date
    if date_columns:
        for col in date_columns:
            if col in df_clean.columns:
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                except Exception as e:
                    st.warning(f"Erreur lors de la conversion de {col} en date: {str(e)}")
    
    # Convertir les colonnes numériques
    if numeric_columns:
        for col in numeric_columns:
            if col in df_clean.columns:
                try:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                except Exception as e:
                    st.warning(f"Erreur lors de la conversion de {col} en nombre: {str(e)}")
    
    # Convertir les colonnes catégorielles
    if categorical_columns:
        for col in categorical_columns:
            if col in df_clean.columns:
                try:
                    df_clean[col] = df_clean[col].astype(str)
                except Exception as e:
                    st.warning(f"Erreur lors de la conversion de {col} en catégorie: {str(e)}")
    
    # Assurer que les colonnes spécifiques sont dans les plages valides
    if 'year' in df_clean.columns:
        df_clean = df_clean[df_clean['year'].between(1900, 2100, inclusive='both')]
    if 'annees' in df_clean.columns:
        df_clean = df_clean[df_clean['annees'].between(1900, 2100, inclusive='both')]
    if 'month' in df_clean.columns:
        df_clean = df_clean[df_clean['month'].between(1, 12, inclusive='both')]
    if 'mois' in df_clean.columns:
        df_clean = df_clean[df_clean['mois'].between(1, 12, inclusive='both')]
    if 'day' in df_clean.columns:
        df_clean = df_clean[df_clean['day'].between(1, 31, inclusive='both')]
    if 'jour' in df_clean.columns:
        df_clean = df_clean[df_clean['jour'].isin(['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'])]
        
    return df_clean

# Connexion directe à Snowflake
@st.cache_resource
def get_conn():
    try:
        return snowflake.connector.connect(
            user=os.environ["SNOWFLAKE_USER"],
            password=os.environ["SNOWFLAKE_PASSWORD"],
            account=os.environ["SNOWFLAKE_ACCOUNT"],
            warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
            database="BOOKSHOP",
            role=os.environ["SNOWFLAKE_ROLE"]
        )
    except Exception as e:
        st.error(f"Erreur de connexion à Snowflake: {str(e)}")
        return None

@st.cache_data
def load_data():
    try:
        conn = get_conn()
        if conn is None:
            return pd.DataFrame()
        
        df = pd.read_sql("SELECT * FROM MARTS.OBT_SALES", conn)
        if df.empty:
            return pd.DataFrame()
            
        df.columns = [col.lower() for col in df.columns]
        df = df.rename(columns={
            "annees": "year",
            "mois": "month",
            "jour": "day",
            "pu": "unit_price",
            "qte": "quantity",
            "facture_id": "invoice_id",
            "facture_code": "invoice_code",
            "qte_totale": "invoice_quantity_total",
            "total_amount": "amount_total",
            "total_paid": "amount_paid",
            "category_intitule": "category",
            "book_code": "book_id",
            "book_intitule": "book_title",
            "isbn_10": "isbn_10",
            "isbn_13": "isbn_13",
            "customer_code": "customer_id",
            "customer_nom": "customer_name"
        })
        
        # Nettoyer les données
        return sanitize_dataframe(
            df,
            date_columns=['date'] if 'date' in df.columns else [],
            numeric_columns=['year', 'month', 'quantity', 'unit_price', 'amount_total', 'amount_paid'],
            categorical_columns=['category', 'book_title', 'customer_name']
        )
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        st.error(traceback.format_exc())
        return pd.DataFrame()

@st.cache_data
def load_books_mois():
    try:
        conn = get_conn()
        if conn is None:
            return pd.DataFrame()
            
        df = pd.read_sql("SELECT * FROM WAREHOUSE.FACT_BOOKS_MOIS", conn)
        if df.empty:
            return pd.DataFrame()
            
        df.columns = [col.lower() for col in df.columns]
        
        # Nettoyer les données
        return sanitize_dataframe(
            df,
            numeric_columns=['annees', 'mois', 'quantite_totale'],
            categorical_columns=['book_title']
        )
    except Exception as e:
        st.error(f"Erreur lors du chargement des données books_mois: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_books_jour():
    try:
        conn = get_conn()
        if conn is None:
            return pd.DataFrame()
            
        df = pd.read_sql("SELECT * FROM WAREHOUSE.FACT_BOOKS_JOUR", conn)
        if df.empty:
            return pd.DataFrame()
            
        df.columns = [col.lower() for col in df.columns]
        
        # Nettoyer les données
        return sanitize_dataframe(
            df,
            numeric_columns=['annees', 'quantite_totale'],
            categorical_columns=['jour', 'book_title']
        )
    except Exception as e:
        st.error(f"Erreur lors du chargement des données books_jour: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_books_annees():
    try:
        conn = get_conn()
        if conn is None:
            return pd.DataFrame()
            
        df = pd.read_sql("SELECT * FROM WAREHOUSE.FACT_BOOKS_ANNEES", conn)
        if df.empty:
            return pd.DataFrame()
            
        df.columns = [col.lower() for col in df.columns]
        
        # Nettoyer les données
        return sanitize_dataframe(
            df,
            numeric_columns=['annees', 'quantite_totale'],
            categorical_columns=['book_title']
        )
    except Exception as e:
        st.error(f"Erreur lors du chargement des données books_annees: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_fact_ventes():
    try:
        conn = get_conn()
        if conn is None:
            return pd.DataFrame()
            
        df = pd.read_sql("SELECT * FROM WAREHOUSE.FACT_VENTES", conn)
        if df.empty:
            return pd.DataFrame()
            
        df.columns = [col.lower() for col in df.columns]
        
        # Nettoyer les données
        return sanitize_dataframe(
            df,
            date_columns=['date'] if 'date' in df.columns else [],
            numeric_columns=['qte', 'montant', 'pu'],
            categorical_columns=['customer_id', 'book_id']
        )
    except Exception as e:
        st.error(f"Erreur lors du chargement des données fact_ventes: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_fact_factures():
    try:
        conn = get_conn()
        if conn is None:
            return pd.DataFrame()
            
        df = pd.read_sql("SELECT * FROM WAREHOUSE.FACT_FACTURES", conn)
        if df.empty:
            return pd.DataFrame()
            
        df.columns = [col.lower() for col in df.columns]
        
        # Nettoyer les données
        return sanitize_dataframe(
            df,
            date_columns=['date'] if 'date' in df.columns else [],
            numeric_columns=['total_amount', 'total_paid', 'qte_totale'],
            categorical_columns=['customer_id']
        )
    except Exception as e:
        st.error(f"Erreur lors du chargement des données fact_factures: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_dim_books():
    try:
        conn = get_conn()
        if conn is None:
            return pd.DataFrame()
            
        df = pd.read_sql("SELECT * FROM WAREHOUSE.DIM_BOOKS", conn)
        if df.empty:
            return pd.DataFrame()
            
        df.columns = [col.lower() for col in df.columns]
        
        # Nettoyer les données
        return sanitize_dataframe(
            df,
            categorical_columns=['book_id', 'intitule', 'category_id']
        )
    except Exception as e:
        st.error(f"Erreur lors du chargement des données dim_books: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_dim_customers():
    try:
        conn = get_conn()
        if conn is None:
            return pd.DataFrame()
            
        df = pd.read_sql("SELECT * FROM WAREHOUSE.DIM_CUSTOMERS", conn)
        if df.empty:
            return pd.DataFrame()
            
        df.columns = [col.lower() for col in df.columns]
        
        # Nettoyer les données
        return sanitize_dataframe(
            df,
            categorical_columns=['customer_id', 'nom']
        )
    except Exception as e:
        st.error(f"Erreur lors du chargement des données dim_customers: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_dim_category():
    try:
        conn = get_conn()
        if conn is None:
            return pd.DataFrame()
            
        df = pd.read_sql("SELECT * FROM WAREHOUSE.DIM_CATEGORY", conn)
        if df.empty:
            return pd.DataFrame()
            
        df.columns = [col.lower() for col in df.columns]
        
        # Nettoyer les données
        return sanitize_dataframe(
            df,
            categorical_columns=['category_id', 'intitule']
        )
    except Exception as e:
        st.error(f"Erreur lors du chargement des données dim_category: {str(e)}")
        return pd.DataFrame()

# Chargement sécurisé des données
try:
    df = load_data()
    if df.empty:
        st.error("Aucune donnée n'a pu être chargée depuis MARTS.OBT_SALES. Veuillez vérifier votre connexion à Snowflake.")
    
    # Chargement des autres dataframes avec gestion des erreurs
    df_books_mois = load_books_mois()
    df_books_jour = load_books_jour()
    df_books_annees = load_books_annees()
    df_ventes = load_fact_ventes()
    df_factures = load_fact_factures()
    df_dim_books = load_dim_books()
    df_dim_customers = load_dim_customers() 
    df_dim_category = load_dim_category()
    
    # Vérification supplémentaire de toutes les données
    if any(x.empty for x in [df, df_books_mois, df_books_jour, df_books_annees]):
        st.warning("Certaines données n'ont pas pu être chargées ou sont vides. Certaines visualisations peuvent ne pas s'afficher correctement.")
    
except Exception as e:
    st.error(f"Une erreur est survenue lors du chargement des données: {str(e)}")
    st.error(traceback.format_exc())
    
    # Initialiser des DataFrames vides en cas d'erreur
    df = pd.DataFrame()
    df_books_mois = pd.DataFrame() 
    df_books_jour = pd.DataFrame()
    df_books_annees = pd.DataFrame()
    df_ventes = pd.DataFrame()
    df_factures = pd.DataFrame()
    df_dim_books = pd.DataFrame()
    df_dim_customers = pd.DataFrame()
    df_dim_category = pd.DataFrame()

# Interface avec tabs seulement si les données principales sont disponibles
if not df.empty:
    # Interface avec tabs au lieu de radio buttons
    st.sidebar.image("https://img.icons8.com/color/96/000000/open-book--v2.png", width=100)
    st.sidebar.title("Bookshop Analytics")
    st.sidebar.header("Filtres")

    # Filtres avancés
    year = st.sidebar.selectbox("Année", sorted(df["year"].dropna().unique()))
    months = st.sidebar.multiselect("Mois", df["month"].dropna().unique(), default=df["month"].unique())
    categories = st.sidebar.multiselect("Catégorie", df["category"].dropna().unique(), default=df["category"].unique())
    min_price, max_price = st.sidebar.slider(
        "Gamme de prix (FCFA)", 
        int(df["unit_price"].min()), 
        int(df["unit_price"].max()), 
        (int(df["unit_price"].min()), int(df["unit_price"].max()))
    )

    # Filtrage
    df_filtered = df[
        (df["year"] == year) &
        (df["month"].isin(months)) &
        (df["category"].isin(categories)) &
        (df["unit_price"] >= min_price) &
        (df["unit_price"] <= max_price)
    ]

    # Utilisation des tabs pour l'organisation
    tabs = st.tabs([
        "📊 Tableau de bord", 
        "📈 Tendances mensuelles", 
        "📅 Analyse journalière", 
        "🗓️ Vue annuelle",
        "🔍 Analyse détaillée",
        "🔬 Modèles avancés",
        "📁 Export"
    ])

    # Tab 1: Vue globale / Tableau de bord
    with tabs[0]:
        st.title("📚 Tableau de bord - Bookshop")
        
        # Vérifier si df_filtered est valide et non vide
        if df_filtered.empty:
            st.warning("Aucune donnée disponible pour les filtres sélectionnés.")
        else:
            # KPIs en ligne avec style amélioré
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Total ventes", f"{df_filtered['amount_paid'].sum():,.0f} FCFA")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Commandes", df_filtered['invoice_id'].nunique())
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Clients uniques", df_filtered['customer_id'].nunique())
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                avg_order = 0 if df_filtered['invoice_id'].nunique() == 0 else df_filtered['amount_paid'].sum() / df_filtered['invoice_id'].nunique()
                st.metric("Panier moyen", f"{avg_order:,.0f} FCFA")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Visualisations principales
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📘 Top livres vendus")
                top_books = df_filtered.groupby("book_title")["quantity"].sum().sort_values(ascending=False).head(10)
                fig = px.bar(
                    top_books.reset_index(), 
                    y="book_title", 
                    x="quantity", 
                    orientation='h',
                    title="Livres les plus vendus",
                    labels={"book_title": "Titre", "quantity": "Quantité vendue"},
                    color="quantity",
                    color_continuous_scale=px.colors.sequential.Blues
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📚 Répartition par catégorie")
                cat_data = df_filtered.groupby("category")["quantity"].sum().sort_values(ascending=False)
                fig = px.pie(
                    cat_data.reset_index(), 
                    values="quantity", 
                    names="category",
                    title="Ventes par catégorie",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Clients et performance
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👤 Meilleurs clients")
                top_clients = df_filtered.groupby("customer_name")["amount_paid"].sum().sort_values(ascending=False).head(10)
                fig = px.bar(
                    top_clients.reset_index(),
                    x="amount_paid",
                    y="customer_name",
                    orientation='h',
                    labels={"customer_name": "Client", "amount_paid": "Montant des achats (FCFA)"},
                    color="amount_paid",
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("💰 Performance des ventes")
                # Comparaison des ventes par mois pour l'année sélectionnée
                monthly_sales = df_filtered.groupby("month")["amount_paid"].sum().reindex(range(1, 13)).fillna(0)
                fig = px.line(
                    monthly_sales.reset_index(), 
                    x="month", 
                    y="amount_paid",
                    markers=True,
                    labels={"month": "Mois", "amount_paid": "Ventes (FCFA)"},
                    title=f"Évolution des ventes {year}"
                )
                fig.update_xaxes(tickmode='array', tickvals=list(range(1, 13)), ticktext=[calendar.month_abbr[m] for m in range(1, 13)])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
    # Vue par mois (avec visualisations améliorées)
    with tabs[1]:
        st.title("📈 Tendances mensuelles")
        
        # Vérifier si les données nécessaires sont disponibles
        if df_books_mois.empty:
            st.warning("Aucune donnée de vente mensuelle disponible.")
        else:
            try:
                # Filtrage pour l'année sélectionnée
                filtered = df_books_mois[df_books_mois["annees"] == year]
                
                # Vérifier si nous avons des données à afficher
                if not filtered.empty:
                    # Heatmap des ventes mensuelles par livre
                    st.subheader("Ventes mensuelles par livre")
                    
                    # S'assurer que 'mois' est un entier entre 1 et 12
                    filtered['mois'] = pd.to_numeric(filtered['mois'], errors='coerce')
                    # Supprimer les lignes avec des valeurs de mois invalides
                    filtered = filtered[filtered['mois'].between(1, 12)]
                    
                    # Créer le pivot seulement si nous avons des données valides
                    if not filtered.empty:
                        pivot = filtered.pivot_table(index="mois", columns="book_title", values="quantite_totale").fillna(0)
                        
                        # Convertir les index en entiers pour s'assurer qu'ils sont utilisables avec calendar.month_abbr
                        pivot.index = pivot.index.astype(int)
                        
                        # Création des étiquettes de mois de manière sécurisée
                        month_labels = []
                        for m in pivot.index:
                            try:
                                # Vérifier que l'indice est entre 1 et 12
                                if 1 <= m <= 12:
                                    month_labels.append(calendar.month_abbr[m])
                                else:
                                    month_labels.append(f"Mois {m}")  # Étiquette de secours
                            except Exception:
                                month_labels.append(f"Mois {m}")  # Étiquette de secours en cas d'erreur
                        
                        # Création d'une heatmap interactive
                        fig = px.imshow(
                            pivot,
                            labels=dict(x="Livre", y="Mois", color="Quantité"),
                            x=pivot.columns,
                            y=month_labels,
                            color_continuous_scale="Blues"
                        )
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Répartition des ventes par mois
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Ventes totales par mois")
                            monthly_total = filtered.groupby("mois")["quantite_totale"].sum()
                            # Trier par mois
                            monthly_total = monthly_total.sort_index()
                            
                            fig = px.bar(
                                monthly_total.reset_index(),
                                x="mois",
                                y="quantite_totale",
                                labels={"mois": "Mois", "quantite_totale": "Quantité vendue"},
                                color="quantite_totale",
                                color_continuous_scale="Viridis"
                            )
                            # Utiliser les mêmes étiquettes sécurisées pour les mois
                            month_dict = {m: label for m, label in zip(pivot.index, month_labels)}
                            fig.update_xaxes(
                                tickmode='array', 
                                tickvals=list(month_dict.keys()), 
                                ticktext=list(month_dict.values())
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.subheader("Évolution mensuelle par catégorie")
                            # Supposons que nous avons une colonne category
                            monthly_cat = df_filtered.groupby(["month", "category"])["quantity"].sum().reset_index()
                            fig = px.line(
                                monthly_cat,
                                x="month",
                                y="quantity",
                                color="category",
                                markers=True,
                                labels={"month": "Mois", "quantity": "Quantité", "category": "Catégorie"}
                            )
                            fig.update_xaxes(tickmode='array', tickvals=list(range(1, 13)), ticktext=[calendar.month_abbr[m] for m in range(1, 13)])
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Aucune donnée valide de vente mensuelle trouvée pour l'année sélectionnée.")
            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'affichage des tendances mensuelles: {str(e)}")
                if st.checkbox("Afficher les détails de l'erreur"):
                    st.code(traceback.format_exc())
            
    # Vue par jour (avec visualisations améliorées)
    with tabs[2]:
        st.title("📅 Analyse journalière des ventes")
        
        # Vérifier si les données nécessaires sont disponibles
        if df_books_jour.empty:
            st.warning("Aucune donnée de vente journalière disponible.")
        else:
            try:
                # Filtrage pour l'année sélectionnée
                filtered = df_books_jour[df_books_jour["annees"] == year]
                
                # Heatmap de l'affluence par jour
                st.subheader("Affluence par jour de la semaine")
                
                # Réorganisation des jours de la semaine dans l'ordre
                jours_ordre = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
                day_data = filtered.groupby("jour")["quantite_totale"].sum().reindex(jours_ordre).fillna(0)
                
                # Graphe amélioré
                fig = px.bar(
                    day_data.reset_index(),
                    x="jour",
                    y="quantite_totale",
                    title="Quantité de livres vendus par jour de la semaine",
                    labels={"jour": "Jour", "quantite_totale": "Quantité vendue"},
                    color="quantite_totale",
                    color_continuous_scale="Teal",
                    text="quantite_totale"
                )
                
                # Personnalisation
                fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':jours_ordre})
                fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
                
                # Sections complémentaires
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Performance horaire")
                    # Simulons des données horaires (car elles ne sont pas dans le dataset)
                    # Dans un cas réel, vous auriez cette information depuis votre base de données
                    hours = list(range(8, 20))  # Heures d'ouverture, 8h à 19h
                    dummy_hourly_data = [100, 80, 70, 120, 180, 150, 90, 110, 200, 190, 140, 70]
                    
                    fig = px.line(
                        x=hours, 
                        y=dummy_hourly_data,
                        labels={"x": "Heure de la journée", "y": "Ventes moyennes"},
                        title="Répartition horaire des ventes",
                        markers=True
                    )
                    fig.update_layout(xaxis=dict(tickmode='array', tickvals=hours))
                    fig.add_annotation(
                        text="Heures d'affluence: 12h et 18h",
                        xref="paper", yref="paper",
                        x=0.5, y=0.9,
                        showarrow=False,
                        bgcolor="rgba(255, 255, 255, 0.8)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Comparaison Semaine vs. Weekend")
                    # Création d'une variable weekend
                    weekday_weekend = {
                        'lundi': 'Semaine', 'mardi': 'Semaine', 'mercredi': 'Semaine', 
                        'jeudi': 'Semaine', 'vendredi': 'Semaine',
                        'samedi': 'Weekend', 'dimanche': 'Weekend'
                    }
                    
                    # Conversion des jours en semaine/weekend
                    day_mapping = filtered.copy()
                    day_mapping['periode'] = day_mapping['jour'].map(weekday_weekend)
                    periode_data = day_mapping.groupby('periode')['quantite_totale'].sum()
                    
                    # Graphique en secteurs
                    fig = px.pie(
                        values=periode_data.values, 
                        names=periode_data.index,
                        title="Répartition Semaine vs. Weekend",
                        color=periode_data.index,
                        color_discrete_map={'Semaine': '#3B82F6', 'Weekend': '#F97316'},
                        hole=0.4
                    )
                    fig.update_traces(textinfo='percent+label', pull=[0, 0.1])
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Statistique supplémentaire
                    if 'Weekend' in periode_data and 'Semaine' in periode_data:
                        weekend_ratio = periode_data['Weekend'] / (periode_data['Weekend'] + periode_data['Semaine'])
                        weekend_days = 2
                        weekday_days = 5
                        weekend_per_day = periode_data['Weekend'] / weekend_days if weekend_days > 0 else 0
                        weekday_per_day = periode_data['Semaine'] / weekday_days if weekday_days > 0 else 0
                        
                        st.info(f"💡 **Analyse**: Le weekend représente {weekend_ratio:.1%} des ventes totales. "
                              f"En moyenne, un jour de weekend génère {weekend_per_day/weekday_per_day:.1f}x plus de ventes qu'un jour de semaine.")
            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'affichage des données journalières: {str(e)}")
            
    # Vue par année (avec visualisations améliorées)
    with tabs[3]:
        st.title("🗓️ Vue annuelle des performances")
        
        # Vérifier si les données nécessaires sont disponibles
        if df_books_annees.empty:
            st.warning("Aucune donnée de vente annuelle disponible.")
        else:
            try:
                # Graphique principal - Évolution annuelle
                annual = df_books_annees.groupby("annees")["quantite_totale"].sum()
                
                # Calculer la croissance
                annual_growth = annual.pct_change() * 100
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("Évolution des ventes annuelles")
                    fig = px.bar(
                        annual.reset_index(),
                        x="annees",
                        y="quantite_totale",
                        title="Total des ventes par année",
                        labels={"annees": "Année", "quantite_totale": "Quantité vendue"},
                        text="quantite_totale"
                    )
                    # Ajout d'une ligne de tendance
                    fig.add_trace(
                        go.Scatter(
                            x=annual.index, 
                            y=annual.values,
                            mode='lines+markers',
                            name='Tendance',
                            line=dict(color='red', width=2)
                        )
                    )
                    fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Taux de croissance")
                    if len(annual_growth.dropna()) > 0:
                        growth_color = ['red' if x < 0 else 'green' for x in annual_growth.dropna()]
                        fig = px.bar(
                            x=annual_growth.dropna().index,
                            y=annual_growth.dropna().values,
                            title="Croissance annuelle (%)",
                            labels={"x": "Année", "y": "Croissance (%)"},
                            text=[f"{x:.1f}%" for x in annual_growth.dropna().values]
                        )
                        fig.update_traces(marker_color=growth_color, textposition='outside')
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Données insuffisantes pour calculer la croissance.")
                
                # Statistiques additionnelles
                st.subheader("Statistiques clés par année")
                
                # Agréger d'autres métriques par année
                if 'unit_price' in df.columns and 'quantity' in df.columns:
                    yearly_metrics = df.groupby('year').agg({
                        'invoice_id': 'nunique',
                        'customer_id': 'nunique',
                        'quantity': 'sum',
                        'amount_paid': 'sum'
                    }).reset_index()
                    
                    # Calculer des métriques dérivées de manière sécurisée
                    def safe_division(numerator, denominator):
                        try:
                            num = pd.to_numeric(numerator, errors='coerce')
                            den = pd.to_numeric(denominator, errors='coerce')
                            # Gérer NaN et division par zéro
                            if pd.isna(num) or pd.isna(den) or den == 0:
                                return 0
                            return num / den
                        except Exception:
                            return 0 # Retourne 0 en cas d'erreur inattendue

                    yearly_metrics['avg_order_value'] = yearly_metrics.apply(
                        lambda row: safe_division(row['amount_paid'], row['invoice_id']), axis=1
                    )
                    yearly_metrics['avg_customer_value'] = yearly_metrics.apply(
                        lambda row: safe_division(row['amount_paid'], row['customer_id']), axis=1
                    )
                    
                    # Remplacement des colonnes anglaises par françaises pour l'affichage
                    yearly_metrics = yearly_metrics.rename(columns={
                        'year': 'Année',
                        'invoice_id': 'Nombre de commandes',
                        'customer_id': 'Clients uniques',
                        'quantity': 'Quantité vendue',
                        'amount_paid': 'Chiffre d\'affaires (FCFA)',
                        'avg_order_value': 'Valeur moyenne commande (FCFA)',
                        'avg_customer_value': 'Valeur moyenne client (FCFA)'
                    })
                    
                    # Formatage des valeurs monétaires
                    for col in ['Chiffre d\'affaires (FCFA)', 'Valeur moyenne commande (FCFA)', 'Valeur moyenne client (FCFA)']:
                        yearly_metrics[col] = yearly_metrics[col].apply(lambda x: f"{x:,.0f}")
                        
                    st.dataframe(yearly_metrics, use_container_width=True)
            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'affichage des données annuelles: {str(e)}")

    # Tab 4: Analyse détaillée
    with tabs[4]:
        st.title("🔍 Analyse détaillée")
        
        # Vérifier si les données principales sont disponibles
        if df.empty:
            st.warning("Aucune donnée disponible pour l'analyse détaillée.")
        else:
            try:
                # Sous-onglets pour l'analyse détaillée
                detail_tabs = st.tabs(["📚 Livres", "👥 Clients", "💰 Revenus"])
                
                # Sous-onglet Livres
                with detail_tabs[0]:
                    st.subheader("Analyse détaillée des ventes de livres")
                    
                    # Sélecteur de livre
                    all_books = sorted(df['book_title'].unique())
                    selected_book = st.selectbox("Sélectionner un livre", all_books)
                    
                    # Filtrer les données pour le livre sélectionné
                    book_data = df[df['book_title'] == selected_book]
                    
                    # Informations générales sur le livre
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        total_sold = book_data['quantity'].sum()
                        st.metric("Total vendu", f"{total_sold} exemplaires")
                    
                    with col2:
                        total_revenue = book_data['amount_paid'].sum()
                        st.metric("Chiffre d'affaires", f"{total_revenue:,.0f} FCFA")
                    
                    with col3:
                        avg_price = book_data['unit_price'].mean()
                        st.metric("Prix moyen", f"{avg_price:,.0f} FCFA")
                    
                    # Tendance des ventes du livre sur l'année
                    monthly_book_sales = book_data.groupby('month')['quantity'].sum().reindex(range(1, 13)).fillna(0)
                    
                    fig = px.line(
                        monthly_book_sales.reset_index(), 
                        x='month', 
                        y='quantity',
                        title=f"Évolution des ventes de \"{selected_book}\" sur {year}",
                        labels={'month': 'Mois', 'quantity': 'Quantité vendue'},
                        markers=True
                    )
                    fig.update_xaxes(tickmode='array', tickvals=list(range(1, 13)), ticktext=[calendar.month_abbr[m] for m in range(1, 13)])
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Qui achète ce livre?
                    st.subheader("Qui achète ce livre?")
                    book_customers = book_data.groupby('customer_name')['quantity'].sum().sort_values(ascending=False).head(10)
                    
                    fig = px.bar(
                        book_customers.reset_index(),
                        x='quantity',
                        y='customer_name',
                        orientation='h',
                        title="Top acheteurs",
                        labels={'customer_name': 'Client', 'quantity': 'Quantité achetée'}
                    )
                    fig.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                
                # Sous-onglet Clients
                with detail_tabs[1]:
                    st.subheader("Analyse détaillée des clients")
                    
                    # Sélecteur de client
                    all_customers = sorted(df['customer_name'].unique())
                    selected_customer = st.selectbox("Sélectionner un client", all_customers)
                    
                    # Filtrer les données pour le client sélectionné
                    customer_data = df[df['customer_name'] == selected_customer]
                    
                    # Informations générales sur le client
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        total_spent = customer_data['amount_paid'].sum()
                        st.metric("Total dépensé", f"{total_spent:,.0f} FCFA")
                    
                    with col2:
                        total_orders = customer_data['invoice_id'].nunique()
                        st.metric("Nombre de commandes", total_orders)
                    
                    with col3:
                        avg_order = total_spent / total_orders if total_orders > 0 else 0
                        st.metric("Panier moyen", f"{avg_order:,.0f} FCFA")
                    
                    # Historique d'achat
                    st.subheader("Historique d'achat")
                    customer_monthly = customer_data.groupby('month')['amount_paid'].sum().reindex(range(1, 13)).fillna(0)
                    
                    fig = px.bar(
                        customer_monthly.reset_index(),
                        x='month',
                        y='amount_paid',
                        title=f"Dépenses mensuelles de {selected_customer} en {year}",
                        labels={'month': 'Mois', 'amount_paid': 'Montant (FCFA)'}
                    )
                    fig.update_xaxes(tickmode='array', tickvals=list(range(1, 13)), ticktext=[calendar.month_abbr[m] for m in range(1, 13)])
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Quels livres achète ce client?
                    st.subheader("Préférences de lecture")
                    customer_books = customer_data.groupby('book_title')['quantity'].sum().sort_values(ascending=False).head(10)
                    
                    fig = px.pie(
                        customer_books.reset_index(),
                        values='quantity',
                        names='book_title',
                        title="Livres achetés",
                        hole=0.4
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Catégories préférées
                    customer_categories = customer_data.groupby('category')['quantity'].sum().sort_values(ascending=False)
                    
                    fig = px.bar(
                        customer_categories.reset_index(),
                        x='category',
                        y='quantity',
                        title="Catégories préférées",
                        labels={'category': 'Catégorie', 'quantity': 'Quantité achetée'},
                        color='quantity',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Sous-onglet Revenus
                with detail_tabs[2]:
                    st.subheader("Analyse des revenus")
                    
                    # Répartition par catégorie
                    st.subheader("Répartition du chiffre d'affaires par catégorie")
                    category_revenue = df_filtered.groupby('category')['amount_paid'].sum().sort_values(ascending=False)
                    
                    fig = px.pie(
                        category_revenue.reset_index(),
                        values='amount_paid',
                        names='category',
                        title="Distribution du CA par catégorie",
                        color_discrete_sequence=px.colors.sequential.Plasma_r
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Analyse de rentabilité
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Top 10 des produits les plus rentables
                        st.subheader("Produits les plus rentables")
                        product_profit = df_filtered.groupby('book_title')['amount_paid'].sum().sort_values(ascending=False).head(10)
                        
                        fig = px.bar(
                            product_profit.reset_index(),
                            x='amount_paid',
                            y='book_title',
                            orientation='h',
                            title="Top 10 - Revenus par livre",
                            labels={'book_title': 'Livre', 'amount_paid': 'Revenu (FCFA)'},
                            color='amount_paid',
                            color_continuous_scale='Greens'
                        )
                        fig.update_layout(yaxis={'categoryorder':'total ascending'})
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Ratio quantité/revenu
                        st.subheader("Ratio Quantité/Revenu")
                        
                        # Créer un dataframe avec la quantité et le revenu par livre
                        product_ratio = df_filtered.groupby('book_title').agg({
                            'quantity': 'sum',
                            'amount_paid': 'sum'
                        }).reset_index()
                        
                        # Calculer le ratio (revenu par unité)
                        product_ratio['ratio'] = product_ratio['amount_paid'] / product_ratio['quantity']
                        product_ratio = product_ratio.sort_values(by='ratio', ascending=False).head(10)
                        
                        fig = px.bar(
                            product_ratio,
                            x='ratio',
                            y='book_title',
                            orientation='h',
                            title="Livres avec le meilleur rendement par unité",
                            labels={'book_title': 'Livre', 'ratio': 'Revenu par unité (FCFA)'},
                            color='ratio',
                            color_continuous_scale='Reds'
                        )
                        fig.update_layout(yaxis={'categoryorder':'total ascending'})
                        st.plotly_chart(fig, use_container_width=True)
                    
                        # Évolution des revenus
                        st.subheader("Évolution des revenus")
                        revenue_trend = df_filtered.groupby('month')['amount_paid'].sum().reindex(range(1, 13)).fillna(0)
                        
                        fig = px.area(
                            revenue_trend.reset_index(),
                            x='month',
                            y='amount_paid',
                            title=f"Évolution du chiffre d'affaires en {year}",
                            labels={'month': 'Mois', 'amount_paid': 'Chiffre d\'affaires (FCFA)'}
                        )
                        fig.update_xaxes(tickmode='array', tickvals=list(range(1, 13)), ticktext=[calendar.month_abbr[m] for m in range(1, 13)])
                        st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'analyse détaillée: {str(e)}")

    # Tab 5: Modèles avancés - Utilisation des tables dimensionnelles et de faits
    with tabs[5]:
        st.title("🔬 Analyses avancées - Modèles détaillés")
        
        # Vérifier si les données nécessaires sont disponibles
        if all(x.empty for x in [df_dim_books, df_dim_customers, df_dim_category, df_ventes, df_factures]):
            st.warning("Aucune donnée disponible pour les analyses avancées.")
        else:
            try:
                # Créer des sous-onglets
                adv_tabs = st.tabs(["📚 Catalogue", "👥 Clients", "🧾 Factures", "📊 Ventes détaillées"])
                
                # Sous-onglet Catalogue (utilisant dim_books et dim_category)
                with adv_tabs[0]:
                    st.subheader("Catalogue complet des livres")
                    
                    # Jointure entre dim_books et dim_category
                    if 'category_id' in df_dim_books.columns and 'category_id' in df_dim_category.columns:
                        catalogue = pd.merge(
                            df_dim_books, 
                            df_dim_category, 
                            on='category_id', 
                            how='left'
                        )
                        
                        # Afficher le catalogue avec filtre par catégorie
                        all_categories = ['Toutes'] + sorted(df_dim_category['intitule'].unique().tolist())
                        selected_cat = st.selectbox("Filtrer par catégorie", all_categories)
                        
                        if selected_cat != 'Toutes':
                            filtered_catalogue = catalogue[catalogue['intitule'] == selected_cat]
                        else:
                            filtered_catalogue = catalogue
                            
                        # Afficher le catalogue
                        st.dataframe(filtered_catalogue, use_container_width=True)
                        
                        # Distribution des livres par catégorie
                        st.subheader("Distribution des livres par catégorie")
                        cat_counts = catalogue.groupby('intitule').size().reset_index(name='count')
                        
                        fig = px.pie(
                            cat_counts, 
                            values='count', 
                            names='intitule',
                            title="Répartition des livres par catégorie"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Les colonnes nécessaires pour joindre dim_books et dim_category ne sont pas disponibles.")
                
                # Sous-onglet Clients (utilisant dim_customers)
                with adv_tabs[1]:
                    st.subheader("Base de données clients")
                    
                    # Afficher les données clients
                    st.dataframe(df_dim_customers, use_container_width=True)
                    
                    # Enrichir avec des statistiques d'achat depuis fact_ventes
                    if 'customer_id' in df_dim_customers.columns and 'customer_id' in df_ventes.columns:
                        # Agréger les achats par client
                        customer_stats = df_ventes.groupby('customer_id').agg({
                            'vente_id': 'count',
                            'qte': 'sum',
                            'montant': 'sum'
                        }).reset_index()
                        
                        customer_stats = customer_stats.rename(columns={
                            'vente_id': 'nb_achats',
                            'qte': 'quantite_totale',
                            'montant': 'montant_total'
                        })
                        
                        # Joindre avec les données clients
                        customer_enriched = pd.merge(
                            df_dim_customers,
                            customer_stats,
                            on='customer_id',
                            how='left'
                        )
                        
                        # Remplacer les NaN par 0 pour les clients sans achat
                        customer_enriched['nb_achats'] = customer_enriched['nb_achats'].fillna(0)
                        customer_enriched['quantite_totale'] = customer_enriched['quantite_totale'].fillna(0)
                        customer_enriched['montant_total'] = customer_enriched['montant_total'].fillna(0)
                        
                        # Segmentation des clients
                        def segment_client(row):
                            if row['montant_total'] == 0:
                                return 'Inactif'
                            elif row['montant_total'] < 10000:
                                return 'Petit acheteur'
                            elif row['montant_total'] < 50000:
                                return 'Acheteur régulier'
                            else:
                                return 'Grand acheteur'
                        
                        customer_enriched['segment'] = customer_enriched.apply(segment_client, axis=1)
                        
                        # Visualiser la segmentation
                        st.subheader("Segmentation des clients")
                        segment_counts = customer_enriched['segment'].value_counts().reset_index()
                        segment_counts.columns = ['segment', 'count']
                        
                        fig = px.pie(
                            segment_counts,
                            values='count',
                            names='segment',
                            title="Répartition des clients par segment",
                            color='segment',
                            color_discrete_map={
                                'Inactif': '#E5E5E5',
                                'Petit acheteur': '#90CAF9',
                                'Acheteur régulier': '#42A5F5',
                                'Grand acheteur': '#1565C0'
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Top clients
                        st.subheader("Top 10 des clients par montant d'achat")
                        top_customers = customer_enriched.sort_values('montant_total', ascending=False).head(10)
                        
                        fig = px.bar(
                            top_customers,
                            x='montant_total',
                            y='nom',
                            orientation='h',
                            title="Top 10 des clients par montant d'achat",
                            labels={'montant_total': 'Montant total (FCFA)', 'nom': 'Client'}
                        )
                        fig.update_layout(yaxis={'categoryorder':'total ascending'})
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Les colonnes nécessaires pour joindre dim_customers et fact_ventes ne sont pas disponibles.")
                
                # Sous-onglet Factures (utilisant fact_factures)
                with adv_tabs[2]:
                    st.subheader("Analyse des factures")
                    
                    # Statistiques des factures
                    if 'total_paid' in df_factures.columns and 'total_amount' in df_factures.columns:
                        factures_stats = {
                            'Nombre total de factures': len(df_factures),
                            'Montant moyen': f"{df_factures['total_amount'].mean():,.0f} FCFA",
                            'Montant médian': f"{df_factures['total_amount'].median():,.0f} FCFA",
                            'Montant minimum': f"{df_factures['total_amount'].min():,.0f} FCFA",
                            'Montant maximum': f"{df_factures['total_amount'].max():,.0f} FCFA",
                            'Écart entre montant et paiement': f"{(df_factures['total_amount'] - df_factures['total_paid']).sum():,.0f} FCFA"
                        }
                        
                        # Afficher les statistiques
                        col1, col2 = st.columns(2)
                        for i, (k, v) in enumerate(factures_stats.items()):
                            if i % 2 == 0:
                                col1.metric(k, v)
                            else:
                                col2.metric(k, v)
                        
                        # Distribution des montants de facture
                        st.subheader("Distribution des montants de facture")
                        
                        fig = px.histogram(
                            df_factures,
                            x='total_amount',
                            nbins=20,
                            title="Distribution des montants de facture",
                            labels={'total_amount': 'Montant total (FCFA)'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Factures par date
                        if 'date' in df_factures.columns:
                            st.subheader("Nombre de factures par jour")
                            df_factures['date'] = pd.to_datetime(df_factures['date'])
                            factures_per_day = df_factures.groupby(df_factures['date'].dt.date).size().reset_index(name='count')
                            
                            fig = px.line(
                                factures_per_day,
                                x='date',
                                y='count',
                                title="Nombre de factures par jour",
                                labels={'date': 'Date', 'count': 'Nombre de factures'},
                                markers=True
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Les colonnes nécessaires dans fact_factures ne sont pas disponibles.")
                
                # Sous-onglet Ventes détaillées (utilisant fact_ventes)
                with adv_tabs[3]:
                    st.subheader("Analyse détaillée des ventes")
                    
                    # Série temporelle des ventes
                    if 'date' in df_ventes.columns and 'montant' in df_ventes.columns:
                        df_ventes['date'] = pd.to_datetime(df_ventes['date'])
                        ventes_par_jour = df_ventes.groupby(df_ventes['date'].dt.date)['montant'].sum().reset_index()
                        
                        fig = px.line(
                            ventes_par_jour,
                            x='date',
                            y='montant',
                            title="Évolution des ventes quotidiennes",
                            labels={'date': 'Date', 'montant': 'Montant des ventes (FCFA)'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Ventes par livre
                        if 'book_id' in df_ventes.columns and 'qte' in df_ventes.columns:
                            top_ventes_par_livre = df_ventes.groupby('book_id')['qte'].sum().sort_values(ascending=False).head(10)
                            
                            # Joindre avec les titres des livres si disponible
                            if 'book_id' in df_dim_books.columns and 'intitule' in df_dim_books.columns:
                                top_livres = pd.merge(
                                    top_ventes_par_livre.reset_index(),
                                    df_dim_books[['book_id', 'intitule']],
                                    on='book_id',
                                    how='left'
                                )
                                
                                fig = px.bar(
                                    top_livres,
                                    x='qte',
                                    y='intitule',
                                    orientation='h',
                                    title="Top 10 des livres les plus vendus",
                                    labels={'qte': 'Quantité vendue', 'intitule': 'Titre du livre'}
                                )
                                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Les colonnes nécessaires pour joindre avec les titres de livres ne sont pas disponibles.")
                        else:
                            st.info("Les colonnes nécessaires dans fact_ventes ne sont pas disponibles.")
            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'analyse avancée: {str(e)}")

    # Tab 6: Export
    with tabs[6]:
        st.title("📁 Export des données")
        
        # Vérifier si df_filtered est valide
        if df_filtered.empty:
            st.warning("Aucune donnée disponible pour l'export.")
        else:
            # Options d'export
            export_type = st.radio("Sélectionner le format d'export", ["CSV", "Excel", "JSON"])
            include_all = st.checkbox("Inclure toutes les colonnes", value=False)
            
            if include_all:
                export_df = df_filtered
            else:
                # Sélection des colonnes par défaut pour l'export
                default_columns = ['invoice_id', 'invoice_code', 'year', 'month', 'day', 'book_title', 
                                  'category', 'quantity', 'unit_price', 'amount_paid', 'customer_name']
                export_df = df_filtered[default_columns]
            
            # Aperçu des données à exporter
            st.subheader("Aperçu")
            st.dataframe(export_df.head(10), use_container_width=True)
            
            # Information sur le nombre de lignes
            st.info(f"L'export contiendra {export_df.shape[0]} lignes et {export_df.shape[1]} colonnes.")
            
            # Boutons d'export
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export CSV
                csv = export_df.to_csv(index=False).encode('utf-8')
                csv_name = f"bookshop_data_{year}_{'-'.join(map(str, months))}.csv"
                st.download_button("📥 Télécharger en CSV", csv, csv_name, "text/csv")
            
            with col2:
                # Export JSON
                # Note: Dans un environnement réel, vous devriez implémenter l'export Excel
                # avec pandas et BytesIO
                json_data = export_df.to_json(orient='records')
                json_name = f"bookshop_data_{year}_{'-'.join(map(str, months))}.json"
                st.download_button("📥 Télécharger en JSON", json_data, json_name, "application/json")
            
            with col3:
                # Information pour Excel (simulation)
                st.info("L'export Excel sera disponible dans une version future.")

    # Ajout d'un footer
    st.markdown("""
    ---
    📊 Dashboard Bookshop | ©️ 2025 | Développé avec Streamlit
    """)
else:
    st.title("❌ Erreur de chargement des données")
    st.error("Impossible de charger les données principales. Veuillez vérifier votre connexion à Snowflake et la qualité des données.")
    st.info("Vérifiez que les tables dans Snowflake contiennent des données valides et correspondent aux schémas attendus.")
    
    # Ajout d'un bouton pour recharger la page
    if st.button("Recharger la page"):
        st.experimental_rerun()
