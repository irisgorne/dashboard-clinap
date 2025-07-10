# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Painel Interativo - Projeto CLiNAP-G")

# Carrega os dados
df = pd.read_csv("data/base_resultado.csv")

# Filtros dinâmicos com opção "Todos"
st.sidebar.header("🔍 Filtros")

def adicionar_opcao_todos(coluna):
    opcoes = df[coluna].dropna().unique().tolist()
    return ["Todos"] + sorted(opcoes)

coluna_filtro_1 = st.sidebar.selectbox("Filtrar por:", df.select_dtypes(include='object').columns, index=0)
valor_filtro_1 = st.sidebar.selectbox("Valor:", adicionar_opcao_todos(coluna_filtro_1))

coluna_filtro_2 = st.sidebar.selectbox("Filtrar também por:", df.select_dtypes(include='object').columns, index=1)
valor_filtro_2 = st.sidebar.selectbox("Valor:", adicionar_opcao_todos(coluna_filtro_2))

# Aplica os filtros apenas se valor for diferente de "Todos"
df_filtrado = df.copy()
if valor_filtro_1 != "Todos":
    df_filtrado = df_filtrado[df_filtrado[coluna_filtro_1] == valor_filtro_1]
if valor_filtro_2 != "Todos":
    df_filtrado = df_filtrado[df_filtrado[coluna_filtro_2] == valor_filtro_2]

# Variáveis numéricas para o gráfico
st.sidebar.markdown("---")
st.sidebar.subheader("📌 Variáveis para Análise")

colunas_numericas = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
x_var = st.sidebar.selectbox("Eixo X:", colunas_numericas, index=1)
y_var = st.sidebar.selectbox("Eixo Y:", colunas_numericas, index=2)

# Gráfico de dispersão com cluster
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
