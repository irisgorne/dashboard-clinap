import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.markdown("<h2 style='text-align: center;'>📊 Painel Interativo - Clustering Nutricional</h2>", unsafe_allow_html=True)

# Carrega os dados
df = pd.read_csv("data/base_resultado.csv")

# ---- Filtros desejados ----
st.sidebar.header("🔍 Filtros")
colunas_filtro = ["Sexo", "Idade", "Região", "Cluster_CLiNAP", "Cluster_CLiNAP_G"]

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

# ---- Eixos do gráfico ----
st.sidebar.markdown("---")
st.sidebar.subheader("📌 Variáveis nutricionais para o gráfico")
variaveis_nutricionais = [col for col in ["IMC", "HbA1c", "Calorias"] if col in df.columns]
x_var = st.sidebar.selectbox("Eixo X:", variaveis_nutricionais, index=0)
y_var = st.sidebar.selectbox("Eixo Y:", variaveis_nutricionais, index=1)

# Escolha do cluster
st.sidebar.markdown("---")
cluster_coluna = st.sidebar.radio("🧠 Agrupamento:", ["Cluster_CLiNAP", "Cluster_CLiNAP_G"])
df_filtrado[cluster_coluna] = df_filtrado[cluster_coluna].astype(str)

# ---- CLASSIFICAÇÃO AUTOMÁTICA DE RISCO POR CLUSTER ----
try:
    medias = df.groupby(cluster_coluna)[["IMC", "HbA1c"]].mean()
    medias["risco_score"] = medias["IMC"] + medias["HbA1c"]
    ordenado = medias.sort_values("risco_score", ascending=False)
    mapeamento_risco = {str(cluster): risco for risco, cluster in zip(["Alto risco", "Intermediário", "Baixo risco"], ordenado.index)}
    df["Classificacao"] = df[cluster_coluna].astype(str).map(mapeamento_risco)
    df_filtrado["Classificacao"] = df_filtrado[cluster_coluna].astype(str).map(mapeamento_risco)
except Exception as e:
    st.warning(f"Erro ao classificar risco automaticamente: {e}")

# ---- Gráfico de dispersão ----
st.markdown(f"<h4 style='text-align: center;'>🔁 Dispersão de {x_var} vs {y_var} por {cluster_coluna}</h4>", unsafe_allow_html=True)

fig = px.scatter(
    df_filtrado,
    x=x_var,
    y=y_var,
    color=cluster_coluna,
    symbol=cluster_coluna,
    hover_data=["ID", "Sexo", "Região", "Idade", "IMC", "Calorias", "HbA1c", "Classificacao"],
)

fig.update_layout(
    xaxis_title=x_var,
    yaxis_title=y_var,
    title=dict(text=f"{x_var} vs {y_var} agrupados por {cluster_coluna}", font=dict(size=16)),
    font=dict(size=11),
    legend_title="Cluster",
    legend=dict(
        orientation="v", yanchor="top", y=1,
        xanchor="left", x=1.02,
        font=dict(size=10),
        bgcolor='rgba(255,255,255,0)', bordercolor='gray', borderwidth=0
    ),
    template="simple_white",
    width=700, height=450,
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# ---- Escore de risco individual visual, filtro e classificação ----
if all(col in df_filtrado.columns for col in ["IMC", "HbA1c"]):
    imc_max = df["IMC"].max()
    hba1c_max = df["HbA1c
