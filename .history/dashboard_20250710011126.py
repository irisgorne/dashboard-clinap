# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Painel Interativo - Clustering Nutricional")

# Carrega os dados
df = pd.read_csv("data/base_resultado.csv")

# ---- Filtros desejados ----
st.sidebar.header("🔍 Filtros")
colunas_filtro = ["Sexo", "Idade", "Região", "Cluster_CLiNAP", "Cluster_CLiNAP_G"]

def opcoes_com_todos(coluna):
    opcoes = df[coluna].dropna().unique().tolist()
    return ["Todos"] + sorted(opcoes)

# Filtros principais
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

# ---- Eixos de análise ----
st.sidebar.markdown("---")
st.sidebar.subheader("📌 Variáveis nutricionais para o gráfico")

variaveis_nutricionais = ["Peso", "IMC", "HbA1c", "Calorias"]
x_var = st.sidebar.selectbox("Eixo X:", variaveis_nutricionais, index=0)
y_var = st.sidebar.selectbox("Eixo Y:", variaveis_nutricionais, index=1)

# Escolha do algoritmo de cluster
st.sidebar.markdown("---")
cluster_coluna = st.sidebar.radio("🧠 Agrupamento:", ["Cluster_CLiNAP", "Cluster_CLiNAP_G"])

# ---- Gráfico de dispersão ----
st.subheader(f"🔁 Dispersão de {x_var} vs {y_var} por {cluster_coluna}")

fig = px.scatter(
    df_filtrado,
    x=x_var,
    y=y_var,
    color=cluster_coluna,
    symbol=cluster_coluna,  # diferentes marcadores
    hover_data=[col for col in ["ID", "Sexo", "Região", "Idade", "Peso", "IMC", "Calorias", "HbA1c"] if col in df.columns],
    title=f"{x_var} vs {y_var} agrupados por {cluster_coluna}",
)

# Melhorias visuais
fig.update_layout(
    xaxis_title=x_var,
    yaxis_title=y_var,
    legend_title="Cluster",
    template="simple_white",
    width=1000,
    height=600,
    margin=dict(l=40, r=40, t=40, b=40)
)

# Corrige escala do eixo se necessário
if "CLiNAP" in cluster_coluna:
    fig.update_xaxes(tickmode='auto', nticks=10)
    fig.update_yaxes(tickmode='auto', nticks=10)

st.plotly_chart(fig, use_container_width=True)

# ---- Tabela abaixo do gráfico ----
st.markdown("### 🧾 Tabela com dados filtrados")
st.dataframe(df_filtrado, use_container_width=True)
