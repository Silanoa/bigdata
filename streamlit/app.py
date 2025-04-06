import streamlit as st
import pandas as pd
import snowflake.connector
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="📊 Dashboard Bookshop", layout="wide")

# Connexion directe à Snowflake
@st.cache_resource
def get_conn():
    return snowflake.connector.connect(
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database="BOOKSHOP",
        role=os.environ["SNOWFLAKE_ROLE"]
    )

@st.cache_data
def load_data():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM STAGING_MARTS.OBT_SALES", conn)
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
    return df

@st.cache_data
def load_books_mois():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM STAGING_WAREHOUSE.FACT_BOOKS_MOIS", conn)
    df.columns = [col.lower() for col in df.columns]
    return df

@st.cache_data
def load_books_jour():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM STAGING_WAREHOUSE.FACT_BOOKS_JOUR", conn)
    df.columns = [col.lower() for col in df.columns]
    return df

@st.cache_data
def load_books_annees():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM STAGING_WAREHOUSE.FACT_BOOKS_ANNEES", conn)
    df.columns = [col.lower() for col in df.columns]
    return df

# Chargement
df = load_data()
df_books_mois = load_books_mois()
df_books_jour = load_books_jour()
df_books_annees = load_books_annees()

# Interface
onglet = st.sidebar.radio("Choisir une vue", ["Vue globale", "Par mois", "Par jour", "Par année", "Exporter"])
st.sidebar.header("Filtres")

# Filtres
year = st.sidebar.selectbox("Année", sorted(df["year"].dropna().unique()))
months = st.sidebar.multiselect("Mois", df["month"].dropna().unique(), default=df["month"].unique())
categories = st.sidebar.multiselect("Catégorie", df["category"].dropna().unique(), default=df["category"].unique())

# Filtrage
df_filtered = df[
    (df["year"] == year) &
    (df["month"].isin(months)) &
    (df["category"].isin(categories))
    ]

# Vue globale
if onglet == "Vue globale":
    st.title("📚 Tableau de bord - Bookshop")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total ventes", f"{df_filtered['amount_paid'].sum():,.0f} FCFA")
    col2.metric("Commandes", df_filtered.shape[0])
    col3.metric("Clients uniques", df_filtered['customer_id'].nunique())

    st.subheader("📘 Top livres vendus")
    top_books = df_filtered.groupby("book_title")["quantity"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_books)

    st.subheader("👤 Meilleurs clients")
    top_clients = df_filtered.groupby("customer_name")["amount_paid"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_clients)

    st.subheader("📚 Répartition par catégorie")
    cat_data = df_filtered.groupby("category")["quantity"].sum().sort_values(ascending=False)
    fig1, ax1 = plt.subplots()
    ax1.pie(cat_data, labels=cat_data.index, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

# Vue par mois
elif onglet == "Par mois":
    st.title("📈 Ventes par mois")
    filtered = df_books_mois[df_books_mois["annees"] == year]
    pivot = filtered.pivot(index="mois", columns="book_title", values="quantite_totale").fillna(0)
    st.line_chart(pivot)

# Vue par jour
elif onglet == "Par jour":
    st.title("📅 Répartition des ventes par jour de la semaine")
    filtered = df_books_jour[df_books_jour["annees"] == year]
    day_data = filtered.groupby("jour")["quantite_totale"].sum().reindex([
        "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"])
    st.bar_chart(day_data)

# Vue par année
elif onglet == "Par année":
    st.title("🗓️ Vue annuelle des ventes")
    annual = df_books_annees.groupby("annees")["quantite_totale"].sum()
    st.line_chart(annual)

# Export
elif onglet == "Exporter":
    st.title("📁 Export des données")
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger les ventes filtrées (CSV)", csv, "ventes_filtrees.csv", "text/csv")
