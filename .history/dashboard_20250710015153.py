# dashboard.py

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

# ---- Classificação de risco por cluster ----
def classificar_risco(cluster):
    if cluster == '2':
        return "Alto risco"
    elif cluster == '1':
        return "Intermediário"
    else:
        return "Baixo risco"

df_filtrado["Classificacao"] = df_filtrado[cluster_coluna].apply(classificar_risco)

# ---- Gráfico de dispersão ----
st.markdown(f"<h4 style='text-align: center;'>🔁 Dispersão de {x_var} vs {y_var} por {cluster_coluna}</h4>", unsafe_allow_html=True)

fig = px.scatter(
    df_filtrado,
    x=x_var,
    y=y_var,
    color=cluster_coluna,
    symbol=cluster_coluna,
    hover_data=[col for col in ["ID", "Sexo", "Região", "Idade", "IMC", "Calorias", "HbA1c", "Classificacao"] if col in df.columns],
    title=f"{x_var} vs {y_var} agrupados por {cluster_coluna}",
)

fig.update_layout(
    xaxis_title=x_var,
    yaxis_title=y_var,
    title=dict(
        text=f"{x_var} vs {y_var} agrupados por {cluster_coluna}",
        font=dict(size=16)
    ),
    font=dict(size=11),
    legend_title="Cluster",
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
        font=dict(size=10),
        bgcolor='rgba(255,255,255,0)',
        bordercolor='gray',
        borderwidth=0
    ),
    template="simple_white",
    width=700,
    height=450,
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# ---- Legenda interpretativa abaixo do gráfico ----
st.markdown("#### 🧠 Interpretação dos Clusters:")
st.markdown("""
- 🔴 **Cluster 2** → Alto risco metabólico (IMC/HbA1c elevados)
- 🔵 **Cluster 1** → Perfil intermediário, heterogêneo
- 🔷 **Cluster 0** → Possível grupo de baixo risco ou bem controlado
""")

# ---- Resumo estatístico por classificação ----
st.markdown("### 📊 Resumo por Classificação de Risco:")
variaveis_resumo = ["IMC", "HbA1c", "Calorias"]
if "Classificacao" in df_filtrado.columns:
    resumo = df_filtrado.groupby("Classificacao")[variaveis_resumo].agg(["mean", "std", "min", "max"]).round(2)
    st.dataframe(resumo)

# ---- Painel Resumo com Contagem e Proporções ----
st.markdown("## 📌 Painel Resumo por Cluster")
col1, col2, col3 = st.columns(3)

with col1:
    total = len(df_filtrado)
    st.metric("👥 Total de Pacientes", total)

with col2:
    if "Classificacao" in df_filtrado.columns:
        alto = (df_filtrado["Classificacao"] == "Alto risco").sum()
        st.metric("🚨 Alto Risco", f"{alto} ({(alto/total*100):.1f}%)")

with col3:
    intermediario = (df_filtrado["Classificacao"] == "Intermediário").sum()
    st.metric("⚠️ Intermediário", f"{intermediario} ({(intermediario/total*100):.1f}%)")

# ---- Gráfico de Barras: Distribuição por Cluster ----
st.markdown("### 📊 Distribuição de Pacientes por Cluster")
contagem_clusters = df_filtrado[cluster_coluna].value_counts().reset_index()
contagem_clusters.columns = ["Cluster", "Contagem"]
fig_bar = px.bar(contagem_clusters, x="Cluster", y="Contagem", color="Cluster", text="Contagem")
fig_bar.update_layout(template="simple_white", width=700, height=400)
st.plotly_chart(fig_bar, use_container_width=True)

# ---- Gráfico de Pizza: Proporção por Sexo ----
st.markdown("### 🧬 Proporção por Sexo")
if "Sexo" in df_filtrado.columns:
    sexo_count = df_filtrado["Sexo"].value_counts().reset_index()
    sexo_count.columns = ["Sexo", "Total"]
    fig_pizza = px.pie(sexo_count, names="Sexo", values="Total", hole=0.4)
    fig_pizza.update_traces(textinfo='percent+label')
    fig_pizza.update_layout(template="simple_white", width=500, height=400)
    st.plotly_chart(fig_pizza, use_container_width=True)

# ---- Botão de Exportação CSV ----
st.markdown("### 💾 Exportar dados filtrados")
csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Baixar CSV com os dados filtrados",
    data=csv,
    file_name="dados_filtrados.csv",
    mime="text/csv"
)

# ---- Tabela com os dados filtrados ----
st.markdown("### 🧾 Tabela com dados filtrados")
st.dataframe(df_filtrado, use_container_width=True)
