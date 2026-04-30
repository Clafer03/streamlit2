import streamlit as st
from pymongo import MongoClient
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="MongoDB Dashboard", layout="wide")

st.title("📊 Dashboard - MongoDB Atlas (sample_analytics)")

# -----------------------------
# CONEXIÓN A MONGO
# -----------------------------
@st.cache_resource
def get_data():
    uri =  st.secrets["mongo"]["url"]
    client = MongoClient(uri)

    db = client["sample_analytics"]
    collection = db["customers"]

    data = list(collection.find().limit(1000))
    df = pd.DataFrame(data)

    return df

df = get_data()

# -----------------------------
# LIMPIEZA
# -----------------------------
if "_id" in df.columns:
    df = df.drop(columns=["_id"])

# Expandir campos anidados si existen
if "accounts" in df.columns:
    df["num_accounts"] = df["accounts"].apply(lambda x: len(x) if isinstance(x, list) else 0)

if "tier_and_details" in df.columns:
    df["num_products"] = df["tier_and_details"].apply(lambda x: len(x) if isinstance(x, dict) else 0)

# -----------------------------
# SIDEBAR FILTROS
# -----------------------------
st.sidebar.header("Filtros")

min_accounts = int(df["num_accounts"].min())
max_accounts = int(df["num_accounts"].max())

account_filter = st.sidebar.slider(
    "Número de cuentas",
    min_accounts,
    max_accounts,
    (min_accounts, max_accounts)
)

# Aplicar filtro
filtered_df = df[
    (df["num_accounts"] >= account_filter[0]) &
    (df["num_accounts"] <= account_filter[1])
]

# -----------------------------
# KPIs
# -----------------------------
st.subheader("📌 Métricas generales")

col1, col2, col3 = st.columns(3)

col1.metric("Clientes", len(filtered_df))
col2.metric("Promedio cuentas", round(filtered_df["num_accounts"].mean(), 2))
col3.metric("Máx cuentas", filtered_df["num_accounts"].max())

# -----------------------------
# GRÁFICOS
# -----------------------------
st.subheader("📈 Distribución de cuentas")

st.bar_chart(filtered_df["num_accounts"].value_counts().sort_index())

st.subheader("📊 Distribución de productos financieros")

if "num_products" in filtered_df.columns:
    st.bar_chart(filtered_df["num_products"].value_counts().sort_index())

# -----------------------------
# TABLA
# -----------------------------
st.subheader("📋 Datos")

st.dataframe(filtered_df.head(100))
