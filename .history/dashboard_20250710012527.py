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

variaveis_nutricionais = [col for col in ["IMC", "HbA1c", "Calorias"] if col in df.columns]
x_var = st.sidebar.selectbox("Eixo X:", variaveis_nutricionais, index=0)
y_var = st.sidebar.selectbox("Eixo Y:", variaveis_nutricionais, index=1)

# Escolha do algoritmo de cluster
st.sidebar.markdown("---")
cluster_coluna = st.sidebar.radio("🧠 Agrupamento:", ["Cluster_CLiNAP", "Cluster_CLiNAP_G"])

# Converte cluster em string para melhor legenda
df_filtrado[cluster_coluna] = df_filtrado[cluster_coluna].astype(str)

# ---- Gráfico de dispersão ----
st.subheader(f"🔁 Dispersão de {x_var} vs {y_var} por {cluster_coluna}")

fig = px.scatter(
    df_filtrado,
    x=x_var,
    y=y_var,
    color=cluster_coluna,
    symbol=cluster_coluna,
    hover_data=[col for col in ["ID", "Sexo", "Região", "Idade", "IMC", "Calorias", "HbA1c"] if col in df.columns],
    title=f"{x_var} vs {y_var} agrupados por {cluster_coluna}",
)

fig.update_layout(
    xaxis_title=x_var,
    yaxis_title=y_var,
    title=dict(
        text=f"{x_var} vs {y_var} agrupados por {cluster_coluna}",
        font=dict(size=18)
    ),
    font=dict(size=12),  # fonte geral
    legend_title="Cluster",
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
        font=dict(size=11),
        bgcolor='rgba(255,255,255,0)',
        bordercolor='gray',
        borderwidth=0
    ),
    template="simple_white",
    width=850,
    height=500,
    margin=dict(l=30, r=30, t=30, b=30)
)


st.plotly_chart(fig, use_container_width=True)

# ---- Tabela abaixo do gráfico ----
st.markdown("### 🧾 Tabela com dados filtrados")
st.dataframe(df_filtrado, use_container_width=True)
