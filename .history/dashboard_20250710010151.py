# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Painel Interativo - Projeto CLiNAP e CLiNAP-G")

# Carrega os dados
df = pd.read_csv("data/base_resultado.csv")

# Detecta colunas de cluster
colunas_cluster = [col for col in df.columns if "cluster" in col.lower()]

# Define colunas categóricas para filtro, mesmo com mais de 15 categorias
colunas_categoricas = df.select_dtypes(include=["object", "category"]).columns.tolist()
colunas_filtro = list(set(colunas_categoricas + colunas_cluster + ["Sexo", "Região", "Objetivo", "NAF", "IMC"]))  # Ajuste conforme necessário

# Filtros
st.sidebar.header("🔍 Filtros")

def opcoes_com_todos(coluna):
    opcoes = df[coluna].dropna().unique().tolist()
    return ["Todos"] + sorted(opcoes)

coluna_filtro_1 = st.sidebar.selectbox("Filtrar por:", colunas_filtro, index=0)
valor_filtro_1 = st.sidebar.selectbox(f"Valor para {coluna_filtro_1}:", opcoes_com_todos(coluna_filtro_1), key="filtro_1")

coluna_filtro_2 = st.sidebar.selectbox("Filtrar também por:", colunas_filtro, index=1)
valor_filtro_2 = st.sidebar.selectbox(f"Valor para {coluna_filtro_2}:", opcoes_com_todos(coluna_filtro_2), key="filtro_2")

# Aplica filtros
df_filtrado = df.copy()
if valor_filtro_1 != "Todos":
    df_filtrado = df_filtrado[df_filtrado[coluna_filtro_1] == valor_filtro_1]
if valor_filtro_2 != "Todos":
    df_filtrado = df_filtrado[df_filtrado[coluna_filtro_2] == valor_filtro_2]

# Variáveis numéricas
st.sidebar.markdown("---")
st.sidebar.subheader("📌 Variáveis para Análise")
colunas_numericas = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

x_var = st.sidebar.selectbox("Eixo X:", colunas_numericas, index=0)
y_var = st.sidebar.selectbox("Eixo Y:", colunas_numericas, index=1)

# Seletor de algoritmo de cluster
st.sidebar.markdown("---")
cluster_coluna = st.sidebar.radio("🧠 Algoritmo de Cluster:", ["Cluster_CLiNAP", "Cluster_CLiNAP_G"])

# Gráfico
st.subheader(f"🔁 Dispersão: {x_var} vs {y_var} por {cluster_coluna}")
fig = px.scatter(
    df_filtrado,
    x=x_var,
    y=y_var,
    color=cluster_coluna,
    symbol=cluster_coluna,  # Diferencia os marcadores
    hover_data=[col for col in ["ID", "Sexo", "Região", "Idade", "Calorias", "HbA1c"] if col in df.columns],
    title=f"Dispersão por Cluster ({cluster_coluna})"
)
st.plotly_chart(fig, use_container_width=True)

# Tabela
st.markdown("### 🧾 Tabela com dados filtrados")
st.dataframe(df_filtrado, us)_
