# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Painel Interativo - Projeto CLiNAP")

# Carrega a base com rótulos
df = pd.read_csv("data/base_resultado.csv")

# Filtros dinâmicos
st.sidebar.header("🔍 Filtros")
coluna_filtro_1 = st.sidebar.selectbox("Filtrar por:", df.columns, index=5)
valor_filtro_1 = st.sidebar.selectbox("Valor:", df[coluna_filtro_1].unique())

coluna_filtro_2 = st.sidebar.selectbox("Filtrar também por:", df.columns, index=6)
valor_filtro_2 = st.sidebar.selectbox("Valor:", df[coluna_filtro_2].unique())

# Aplica os filtros
df_filtrado = df[(df[coluna_filtro_1] == valor_filtro_1) & (df[coluna_filtro_2] == valor_filtro_2)]

# Escolha das variáveis para o gráfico
st.sidebar.markdown("---")
st.sidebar.subheader("📌 Variáveis para Análise")
x_var = st.sidebar.selectbox("Eixo X:", df.select_dtypes(include='number').columns, index=1)
y_var = st.sidebar.selectbox("Eixo Y:", df.select_dtypes(include='number').columns, index=2)

# Gráfico interativo
st.subheader(f"🔁 Dispersão: {x_var} vs {y_var}")
fig = px.scatter(df_filtrado, x=x_var, y=y_var, color="Cluster_CLiNAP_G",
                 hover_data=["ID", "Sexo", "Região", "Idade", "Calorias"])
st.plotly_chart(fig, use_container_width=True)

# Tabela
st.markdown("### 🧾 Tabela Filtrada")
st.dataframe(df_filtrado)
