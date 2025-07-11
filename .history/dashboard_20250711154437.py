import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from sklearn.preprocessing import MinMaxScaler
from src.clinap_g import aplicar_clinap_g
from xhtml2pdf import pisa
import io
import os


st.set_page_config(layout="wide")
st.markdown("<h2 style='text-align: center;'>📊 Painel Interativo - Clustering Nutricional</h2>", unsafe_allow_html=True)


# Carrega os dados
df = pd.read_csv("data/base_resultado.csv")


# Aplica CLiNAP-G
variaveis_g = ["IMC", "HbA1c", "Calorias"]
df_validos = df.dropna(subset=variaveis_g)
X = df_validos[variaveis_g].values
labels_g, pesos_g, penalidade_g, escore_g = aplicar_clinap_g(X, k=3)
scaler = MinMaxScaler(feature_range=(0, 100))
escore_g_normalizado = scaler.fit_transform(escore_g.reshape(-1, 1)).flatten()
df.loc[df_validos.index, "Cluster_CLiNAP_G"] = labels_g
df.loc[df_validos.index, "Escore_CLiNAP_G"] = escore_g_normalizado


# Filtros
st.sidebar.header("🔍 Filtros")
colunas_filtro = ["Sexo", "Idade", "Região", "Cluster_CLiNAP", "Cluster_CLiNAP_G"]
def opcoes_com_todos(col): return ["Todos"] + sorted(df[col].dropna().unique().tolist())
f1 = st.sidebar.selectbox("Filtrar por:", colunas_filtro, index=0)
v1 = st.sidebar.selectbox(f"Valor para {f1}:", opcoes_com_todos(f1), key="filtro_1")
f2 = st.sidebar.selectbox("Filtrar também por:", colunas_filtro, index=1)
v2 = st.sidebar.selectbox(f"Valor para {f2}:", opcoes_com_todos(f2), key="filtro_2")
df_filtrado = df.copy()
if v1 != "Todos": df_filtrado = df_filtrado[df_filtrado[f1] == v1]
if v2 != "Todos": df_filtrado = df_filtrado[df_filtrado[f2] == v2]


# Cluster usado
st.sidebar.markdown("---")
cluster_coluna = st.sidebar.radio("🧠 Agrupamento:", ["Cluster_CLiNAP", "Cluster_CLiNAP_G"])
df_filtrado[cluster_coluna] = df_filtrado[cluster_coluna].astype(str)


# Filtros de eixo X e Y
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Eixos dos Gráficos")
opcoes_numericas = df_filtrado.select_dtypes(include=["float", "int"]).columns.tolist()
eixo_x = st.sidebar.selectbox("Eixo X", opcoes_numericas, index=opcoes_numericas.index("IMC") if "IMC" in opcoes_numericas else 0)
eixo_y = st.sidebar.selectbox("Eixo Y", opcoes_numericas, index=opcoes_numericas.index("HbA1c") if "HbA1c" in opcoes_numericas else 1)


# Escore de risco
if all(col in df_filtrado.columns for col in ["IMC", "HbA1c"]):
    imc_max = df["IMC"].max()
    hba1c_max = df["HbA1c"].max()
    df_filtrado["Escore_risco"] = ((df_filtrado["IMC"] / imc_max) * 0.4 +
                                   (df_filtrado["HbA1c"] / hba1c_max) * 0.6) * 100
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
    escore_min = st.sidebar.slider("Mostrar pacientes com escore igual ou maior que:", 0, 100, 0, step=5)
    df_filtrado = df_filtrado[df_filtrado["Escore_risco"] >= escore_min].sort_values("Escore_risco", ascending=False)


# Gráfico 1 – Dispersão
st.markdown(f"### 🔁 Dispersão: {eixo_x} vs {eixo_y}")
fig_disp = px.scatter(df_filtrado, x=eixo_x, y=eixo_y, color=cluster_coluna,
                      hover_data=["ID", "Sexo", "Idade", "Calorias", "Escore_risco", "Escore_CLiNAP_G"])
st.plotly_chart(fig_disp, use_container_width=True)


# Lista de pacientes
with st.expander("🧬 Lista de pacientes filtrados por escore", expanded=False):
    for _, row in df_filtrado.iterrows():
        st.markdown(f"**ID {row['ID']} - {row['Classificacao']}**")
        st.progress(row['Escore_risco'] / 100)
        st.markdown(f"""
        - **Escore CLiNAP:** {row['Escore_risco']:.1f} ({row['Escore_nivel']})
        - **Escore CLiNAP-G:** {'{:.1f}'.format(row['Escore_CLiNAP_G']) if not pd.isna(row['Escore_CLiNAP_G']) else 'N/A'}
        - **IMC:** {row['IMC']}
        - **HbA1c:** {row['HbA1c']}
        - **Calorias:** {row['Calorias']} kcal
        """)


# Relatório individual
paciente = None
if "ID" in df_filtrado.columns:
    st.markdown("### 📋 Relatório Individual")
    ids_disponiveis = ["-"] + df_filtrado["ID"].dropna().astype(str).tolist()
    id_selecionado = st.selectbox("Selecione o ID:", ids_disponiveis)
    if id_selecionado != "-":
        paciente = df_filtrado[df_filtrado["ID"].astype(str) == id_selecionado].iloc[0]
        st.markdown(f"- **Classificação:** {paciente['Classificacao']}")
        st.markdown(f"- **Escore CLiNAP:** {paciente['Escore_risco']} ({paciente['Escore_nivel']})")
        st.markdown(f"- **Escore CLiNAP-G:** {'{:.1f}'.format(paciente['Escore_CLiNAP_G']) if not pd.isna(paciente['Escore_CLiNAP_G']) else 'N/A'}")
        st.markdown(f"- **IMC:** {paciente['IMC']}  \n- **HbA1c:** {paciente['HbA1c']}  \n- **Calorias:** {paciente['Calorias']}")


# Gráfico 2 – Comparativo
st.markdown(f"### 📉 Comparativo: {eixo_x} vs {eixo_y}")
fig_comp = px.scatter(df_filtrado, x=eixo_x, y=eixo_y, color=cluster_coluna,
                      trendline="ols", template="plotly")
st.plotly_chart(fig_comp, use_container_width=True)


# Gráfico 3 – Histograma
st.markdown("### 📊 Pacientes por Cluster")
fig_hist = px.histogram(df_filtrado, x=cluster_coluna, color=cluster_coluna, text_auto=True)
st.plotly_chart(fig_hist, use_container_width=True)


# Pesos
with st.expander("📊 Pesos CLiNAP-G"):
    for var, peso in zip(variaveis_g, pesos_g):
        st.markdown(f"- **{var}**: `{peso:.4f}`")


# Legenda
with st.expander("📚 Legenda explicativa"):
    st.markdown("""
    **CLiNAP**: IMC e HbA1c com pesos manuais.  
    **CLiNAP-G**: IMC, HbA1c, Calorias com pesos ajustados automaticamente (grafo + coesão).
    """)


# Tabela final
st.markdown("### 🧾 Tabela com dados filtrados")
st.dataframe(df_filtrado, use_container_width=True)


# Exportações
st.markdown("### 💾 Exportações Finais")

# Exportar Painel Completo com gráficos e tabela em PDF (versão compatível com Streamlit Cloud)
with st.expander("📄 Baixar painel completo (gráficos + tabela) em PDF", expanded=False):
    from plotly.io import to_image

    def gerar_html_com_base64():
        # Converter gráficos em imagem base64
        img_disp = base64.b64encode(to_image(fig_disp, format="png")).decode()
        img_comp = base64.b64encode(to_image(fig_comp, format="png")).decode()
        img_hist = base64.b64encode(to_image(fig_hist, format="png")).decode()

        tabela_html = df_filtrado.to_html(index=False, classes='tabela', border=1)

        return f"""
        <html>
        <head>
        <meta charset='utf-8'>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h2, h3 {{ text-align: center; }}
            img {{ display: block; margin: 20px auto; width: 700px; }}
            .tabela {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 30px;
                font-size: 12px;
            }}
            .tabela th, .tabela td {{
                border: 1px solid #000;
                padding: 4px;
                text-align: center;
            }}
            .tabela th {{
                background-color: #f2f2f2;
            }}
        </style>
        </head>
        <body>
            <h2>Painel Completo - CLiNAP</h2>

            <h3>Gráfico 1: Dispersão</h3>
            <img src="data:image/png;base64,{img_disp}">

            <h3>Gráfico 2: Comparativo</h3>
            <img src="data:image/png;base64,{img_comp}">

            <h3>Gráfico 3: Histograma</h3>
            <img src="data:image/png;base64,{img_hist}">

            <h3>Tabela com Dados Filtrados</h3>
            {tabela_html}
        </body>
        </html>
        """

    def converter_html_para_pdf(html_content):
        result = io.BytesIO()
        pisa.CreatePDF(io.StringIO(html_content), dest=result, link_callback=lambda uri, rel: uri)
        return result.getvalue()

    if st.button("📥 Baixar PDF do Painel"):
        try:
            html = gerar_html_com_base64()
            pdf_bytes = converter_html_para_pdf(html)
            b64_pdf = base64.b64encode(pdf_bytes).decode()
            href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="painel_completo.pdf">📄 Clique aqui para baixar</a>'
            st.markdown(href_pdf, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao gerar o PDF: {e}")