# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Título do painel
st.title("🔎 Painel de Perfis Nutricionais")

# Carrega a base simulada
df = pd.read_csv("data/base_simulada.csv")

# Filtros interativos
regiao = st.selectbox("Filtrar por Região:", options=["Todas"] + sorted(df["Região"].unique().tolist()))
sexo = st.radio("Filtrar por Sexo:", options=["Todos", "Feminino", "Masculino"])

# Aplica filtros
df_filtrado = df.copy()
if regiao != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Região"] == regiao]
if sexo != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Sexo"] == sexo]

# Exibe tabela
st.subheader("📋 Tabela de Pacientes Filtrados")
st.dataframe(df_filtrado)

# Gráfico de dispersão
st.subheader("📊 Dispersão: IMC vs HbA1c")
fig = px.scatter(df_filtrado, x="IMC", y="HbA1c", color="Sexo", symbol="Região", size="Calorias", hover_data=["Idade"])
st.plotly_chart(fig, use_container_width=True)
