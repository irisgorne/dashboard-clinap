# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Painel Interativo - Projeto CLiNAP-G")

# Carrega os dados
df = pd.read_csv("data/base_resultado.csv")

# Filtros com "Todos"
st.sidebar.header("🔍 Filtros")

def opcoes_com_todos(coluna):
    opcoes = df[coluna].dropna().unique().tolist()
    return ["Todos"] + sorted(opcoes)

# Colunas categóricas ou discretas para filtros
colunas_filtro = df.columns[df.nunique() < 15].tolist()

coluna_filtro_1 = st.sidebar.selectbox("Filtrar por:", colunas_filtro, index=0)
valor_filtro_1 = st.sidebar.selectbox(f"Valor para {coluna_filtro_1}:", opcoes_com_todos(coluna_filtro_1), key="filtro_1")

coluna_filtro_2 = st.sidebar.selectbox("Filtrar também por:", colunas_filtro, index=1)
valor_filtro_2 = st.sidebar.selectbox(f"Valor para {coluna_filtro_2}:", opcoes_com_todos(coluna_filtro_2), key="filtro_2")

# Aplica filtros somente se valor != "Todos"
df_filtrado = df.copy()
if valor_filtro_1 != "Todos":
    df_filtrado = df_filtrado[df_filtrado[coluna_filtro_1] == valor_filtro_1]
if valor_filtro_2 != "Todos":
    df_filtrado = df_filtrado[df_filtrado[coluna_filtro_2] == valor_filtro_2]

# Escolha de variáveis numéricas para gráfico
st.sidebar.markdown("---")
st.sidebar.subheader("📌 Variáveis para Análise")
colunas_numericas = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

x_var = st.sidebar.selectbox("Eixo X:", colunas_numericas, index=0)
y_var = st.sidebar.selectbox("Eixo Y:", colunas_numericas, index=1)

# Gráfico de dispersão
st.subheader(f"🔁 Dispersão: {x_var} vs {y_var}")
fig = px.scatter(
    df_filtrado,
    x=x_var,
    y=y_var,
    color="Cluster_CLiNAP_G",
    hover_data=["ID", "Sexo", "Região", "Idade", "Calorias", "HbA1c"],
    title="Dispersão por Cluster (CLiNAP-G)"
)
st.plotly_chart(fig, use_container_width=True)

# Tabela
st.markdown("### 🧾 Tabela com dados filtrados")
st.dataframe(df_filtrado, use_container_width=True)
