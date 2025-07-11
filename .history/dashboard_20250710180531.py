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

# ---- Gráfico de dispersão ----
st.markdown(f"<h4 style='text-align: center;'>🔁 Dispersão de {x_var} vs {y_var} por {cluster_coluna}</h4>", unsafe_allow_html=True)

fig = px.scatter(
    df_filtrado,
    x=x_var,
    y=y_var,
    color=cluster_coluna,
    symbol=cluster_coluna,
    hover_data=["ID", "Sexo", "Região", "Idade", "IMC", "Calorias", "HbA1c"],
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
    hba1c_max = df["HbA1c"].max()
    df_filtrado["Escore_risco"] = (
        (df_filtrado["IMC"] / imc_max) * 0.4 +
        (df_filtrado["HbA1c"] / hba1c_max) * 0.6
    ) * 100
    df_filtrado["Escore_risco"] = df_filtrado["Escore_risco"].round(1)

    def escore_nivel(score):
        if score >= 80:
            return "🔴 Alto"
        elif score >= 60:
            return "🟠 Moderado"
        else:
            return "🟢 Baixo"

    def classificar_risco(score):
        if score >= 80:
            return "Alto risco"
        elif score >= 60:
            return "Intermediário"
        else:
            return "Baixo risco"

    df_filtrado["Escore_nivel"] = df_filtrado["Escore_risco"].apply(escore_nivel)
    df_filtrado["Classificacao"] = df_filtrado["Escore_risco"].apply(classificar_risco)

    # Filtro por escore
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Filtro por Escore de Risco")
    escore_min = st.sidebar.slider("Filtrar pacientes com escore igual ou maior que:", 0, 100, 0, step=5)
    df_filtrado = df_filtrado[df_filtrado["Escore_risco"] >= escore_min]

    # Ordenação por risco
    df_filtrado = df_filtrado.sort_values("Escore_risco", ascending=False)

    # Exibição com expander
   with st.expander("🧪 Escore de Risco Individual (0 a 100):", expanded=False):
    for _, row in df_filtrado.iterrows():
        st.markdown(f"**ID {row['ID']} - {row['Classificacao']}**")
        st.progress(row["Escore_risco"] / 100)
        st.markdown(f"""
        - **Escore CLiNAP:** {row['Escore_risco']} ({row['Escore_nivel']})
        - **Escore CLiNAP-G:** {row.get('Escore_CLiNAP_G', 'N/A'):.1f}
        - **IMC:** {row['IMC']}
        - **HbA1c:** {row['HbA1c']}
        - **Calorias:** {row['Calorias']} kcal
        """)


# ---- Relatório individual ----
if "ID" in df_filtrado.columns:
    st.markdown("### 📋 Relatório Individual do Paciente")
    ids_disponiveis = ["-"] + df_filtrado["ID"].dropna().unique().tolist()
id_selecionado = st.selectbox("Selecione um paciente:", ids_disponiveis)

if id_selecionado != "-":
    paciente = df_filtrado[df_filtrado["ID"] == id_selecionado].iloc[0]

    st.markdown("#### Detalhes do Paciente Selecionado")
    st.markdown(f"- **ID:** {paciente['ID']}")
    st.markdown(f"- **Classificação:** {paciente['Classificacao']}")
    st.markdown(f"- **Escore de Risco:** {paciente['Escore_risco']} ({paciente['Escore_nivel']})")
    st.markdown(f"- **IMC:** {paciente['IMC']}")
    st.markdown(f"- **HbA1c:** {paciente['HbA1c']}")
    st.markdown(f"- **Calorias:** {paciente['Calorias']} kcal")

# ---- Exportação e tabela ----
st.markdown("### 💾 Exportar dados filtrados")
csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button("📥 Baixar CSV", data=csv, file_name="dados_filtrados.csv", mime="text/csv")

st.markdown("### 🧾 Tabela com dados filtrados")
st.dataframe(df_filtrado, use_container_width=True)
from sklearn.preprocessing import MinMaxScaler
from src.clinap_g import aplicar_clinap_g  # ajuste o caminho se estiver em outro local

# 🔢 Define as variáveis que farão parte do CLiNAP-G
variaveis_g = ["IMC", "HbA1c", "Calorias"]
df_validos = df.dropna(subset=variaveis_g)
X = df_validos[variaveis_g].values

# ⚙️ Aplica o CLiNAP-G
labels_g, pesos_g, penalidade_g, escore_g = aplicar_clinap_g(X, k=3)

# 🔁 Normaliza o escore para escala 0 a 100
scaler = MinMaxScaler(feature_range=(0, 100))
escore_g_normalizado = scaler.fit_transform(escore_g.reshape(-1, 1)).flatten()

# 🧩 Atualiza o DataFrame original
df.loc[df_validos.index, "Cluster_CLiNAP_G"] = labels_g
df.loc[df_validos.index, "Escore_CLiNAP_G"] = escore_g_normalizado

