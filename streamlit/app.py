import streamlit as st
import pandas as pd
import snowflake.connector
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="📊 Dashboard Bookshop", layout="wide")

# Connexion Snowflake
@st.cache_resource
def get_conn():
    return snowflake.connector.connect(
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database="BOOKSHOP",
        schema="MARTS",
        role=os.environ["SNOWFLAKE_ROLE"]
    )

@st.cache_data
def load_data():
    conn = get_conn()
    return pd.read_sql("SELECT * FROM obt_sales", conn)

@st.cache_data
def load_books_mois():
    conn = get_conn()
    return pd.read_sql("SELECT * FROM WAREHOUSE.fact_books_mois", conn)

@st.cache_data
def load_books_jour():
    conn = get_conn()
    return pd.read_sql("SELECT * FROM WAREHOUSE.fact_books_jour", conn)

@st.cache_data
def load_books_annees():
    conn = get_conn()
    return pd.read_sql("SELECT * FROM WAREHOUSE.fact_books_annees", conn)

# Chargement des données
df = load_data()
df_books_mois = load_books_mois()
df_books_jour = load_books_jour()
df_books_annees = load_books_annees()

# Onglets
onglet = st.sidebar.radio("Choisir une vue", ["Vue globale", "Par mois", "Par jour", "Par année", "Exporter"])

# Filtres généraux
st.sidebar.header("Filtres")
annee = st.sidebar.selectbox("Année", sorted(df["annees"].dropna().unique()))
mois = st.sidebar.multiselect("Mois", df["mois"].dropna().unique(), default=df["mois"].unique())
categorie = st.sidebar.multiselect("Catégorie", df["category"].dropna().unique(), default=df["category"].unique())

# Données filtrées
df_filtered = df[(df["annees"] == annee) & df["mois"].isin(mois) & df["category"].isin(categorie)]

# VUE GLOBALE
if onglet == "Vue globale":
    st.title("📚 Tableau de bord - Bookshop")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total ventes", f"{df_filtered['total_paid'].sum():,.0f} FCFA")
    col2.metric("Commandes", df_filtered.shape[0])
    col3.metric("Clients uniques", df_filtered['customer_code'].nunique())

    st.subheader("📘 Top livres vendus")
    top_books = df_filtered.groupby("book_title")["qte"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_books)

    st.subheader("👤 Meilleurs clients")
    top_clients = df_filtered.groupby("customer_name")["total_paid"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_clients)

    st.subheader("📚 Répartition par catégorie")
    cat_data = df_filtered.groupby("category")["qte"].sum().sort_values(ascending=False)
    fig1, ax1 = plt.subplots()
    ax1.pie(cat_data, labels=cat_data.index, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

# PAR MOIS
elif onglet == "Par mois":
    st.title("📈 Ventes par mois")
    filtered_mois = df_books_mois[df_books_mois["annees"] == annee]
    pivot_mois = filtered_mois.pivot(index="mois", columns="book_title", values="quantite_totale").fillna(0)
    st.line_chart(pivot_mois)

# PAR JOUR
elif onglet == "Par jour":
    st.title("📅 Répartition des ventes par jour de la semaine")
    day_data = df_filtered.groupby("jour")["qte"].sum().reindex([
        "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"])
    st.bar_chart(day_data)

# PAR ANNÉE
elif onglet == "Par année":
    st.title("🗓️ Vue annuelle des ventes")
    annee_data = df_books_annees.groupby("annees")["quantite_totale"].sum()
    st.line_chart(annee_data)

# EXPORTER
elif onglet == "Exporter":
    st.title("📁 Export des données")
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger les ventes filtrées (CSV)", csv, "ventes_filtrees.csv", "text/csv")
