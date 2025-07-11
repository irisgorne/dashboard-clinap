import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from sklearn.preprocessing import MinMaxScaler
from src.clinap_g import aplicar_clinap_g
from xhtml2pdf import pisa
import io

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

# Variáveis nutricionais
st.sidebar.markdown("---")
st.sidebar.subheader("📌 Variáveis nutricionais para o gráfico")
variaveis_nutricionais = ["IMC", "HbA1c", "Calorias"]
x_var = st.sidebar.selectbox("Eixo X:", variaveis_nutricionais, index=0)
y_var = st.sidebar.selectbox("Eixo Y:", variaveis_nutricionais, index=1)

# Cluster usado
st.sidebar.markdown("---")
cluster_coluna = st.sidebar.radio("🧠 Agrupamento:", ["Cluster_CLiNAP", "Cluster_CLiNAP_G"])
df_filtrado[cluster_coluna] = df_filtrado[cluster_coluna].astype(str)

# Dispersão
st.markdown(f"<h4 style='text-align: center;'>🔁 Dispersão de {x_var} vs {y_var} por {cluster_coluna}</h4>", unsafe_allow_html=True)
fig = px.scatter(df_filtrado, x=x_var, y=y_var, color=cluster_coluna, symbol=cluster_coluna,
                 hover_data=["ID", "Sexo", "Região", "Idade", "IMC", "Calorias", "HbA1c"])
fig.update_layout(width=700, height=450, template="simple_white", margin=dict(l=20, r=20, t=20, b=20))
st.plotly_chart(fig, use_container_width=True)

# Escore e Classificação
if all(col in df_filtrado.columns for col in ["IMC", "HbA1c"]):
    imc_max = df["IMC"].max()
    hba1c_max = df["HbA1c"].max()
    df_filtrado["Escore_risco"] = ((df_filtrado["IMC"] / imc_max) * 0.4 + (df_filtrado["HbA1c"] / hba1c_max) * 0.6) * 100
    df_filtrado["Escore_risco"] = df_filtrado["Escore_risco"].round(1)

    def escore_nivel(score):
        if score >= 80: return "🔴 Alto"
        elif score >= 60: return "🟠 Moderado"
        else: return "🟢 Baixo"

    def classificar_risco(score):
        if score >= 80: return "Alto risco"
        elif score >= 60: return "Intermediário"
        else: return "Baixo risco"

    df_filtrado["Escore_nivel"] = df_filtrado["Escore_risco"].apply(escore_nivel)
    df_filtrado["Classificacao"] = df_filtrado["Escore_risco"].apply(classificar_risco)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Filtro por Escore de Risco")
    escore_min = st.sidebar.slider("Filtrar pacientes com escore ≥", 0, 100, 0, step=5)
    df_filtrado = df_filtrado[df_filtrado["Escore_risco"] >= escore_min].sort_values("Escore_risco", ascending=False)

    with st.expander("🧪 Escore de Risco Individual (0 a 100):", expanded=False):
        for _, row in df_filtrado.iterrows():
            st.markdown(f"**ID {row['ID']} - {row['Classificacao']}**")
            st.progress(row['Escore_risco'] / 100)
            st.markdown(f"- **Escore CLiNAP:** {row['Escore_risco']:.1f} ({row['Escore_nivel']})")
            st.markdown(f"- **Escore CLiNAP-G:** {'{:.1f}'.format(row['Escore_CLiNAP_G']) if not pd.isna(row['Escore_CLiNAP_G']) else 'N/A'}")
            st.markdown(f"- **IMC:** {row['IMC']}  \n- **HbA1c:** {row['HbA1c']}  \n- **Calorias:** {row['Calorias']} kcal")

# Relatório individual
if "ID" in df_filtrado.columns:
    st.markdown("### 📋 Relatório Individual do Paciente")
    ids_disponiveis = ["-"] + df_filtrado["ID"].dropna().unique().tolist()
    id_selecionado = st.selectbox("Selecione um paciente:", ids_disponiveis)
    if id_selecionado != "-":
        paciente = df_filtrado[df_filtrado["ID"] == id_selecionado].iloc[0]
        st.markdown("#### Detalhes do Paciente Selecionado")
        st.markdown(f"- **ID:** {paciente['ID']}  \n- **Classificação:** {paciente['Classificacao']}  \n- **Escore CLiNAP:** {paciente['Escore_risco']} ({paciente['Escore_nivel']})  \n- **Escore CLiNAP-G:** {'{:.1f}'.format(paciente['Escore_CLiNAP_G']) if not pd.isna(paciente['Escore_CLiNAP_G']) else 'N/A'}")
        st.markdown(f"- **IMC:** {paciente['IMC']}  \n- **HbA1c:** {paciente['HbA1c']}  \n- **Calorias:** {paciente['Calorias']} kcal")

        # PDF
        def gerar_pdf_html(p):
            return f"""<html><body>
            <h2>Relatório Individual - ID {p['ID']}</h2>
            <p><strong>Classificação:</strong> {p['Classificacao']}</p>
            <p><strong>Escore CLiNAP:</strong> {p['Escore_risco']} ({p['Escore_nivel']})</p>
            <p><strong>Escore CLiNAP-G:</strong> {'{:.1f}'.format(p['Escore_CLiNAP_G']) if not pd.isna(p['Escore_CLiNAP_G']) else 'N/A'}</p>
            <p><strong>IMC:</strong> {p['IMC']}  |  <strong>HbA1c:</strong> {p['HbA1c']}  |  <strong>Calorias:</strong> {p['Calorias']} kcal</p>
            </body></html>"""

        def gerar_pdf_download(html):
            result = io.BytesIO()
            pisa.CreatePDF(io.StringIO(html), dest=result)
            return result.getvalue()

        html_pdf = gerar_pdf_html(paciente)
        pdf_bytes = gerar_pdf_download(html_pdf)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="relatorio_paciente_{paciente["ID"]}.pdf">📄 Baixar Relatório em PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

# Gráfico comparativo com linha de tendência
if "Escore_risco" in df_filtrado.columns and "Escore_CLiNAP_G" in df_filtrado.columns:
    st.markdown("### 📉 Comparativo: Escore CLiNAP vs CLiNAP-G")
    fig_comp = px.scatter(df_filtrado, x="Escore_risco", y="Escore_CLiNAP_G", color=cluster_coluna,
                          trendline="ols", hover_data=["ID", "IMC", "HbA1c", "Calorias"],
                          labels={"Escore_risco": "CLiNAP", "Escore_CLiNAP_G": "CLiNAP-G"})
    st.plotly_chart(fig_comp, use_container_width=True)

# Histograma
if cluster_coluna in df_filtrado.columns:
    st.markdown("### 📊 Distribuição de pacientes por cluster")
    hist = px.histogram(df_filtrado, x=cluster_coluna, color=cluster_coluna,
                        title="Pacientes por Cluster", text_auto=True)
    hist.update_layout(bargap=0.3, template="simple_white")
    st.plotly_chart(hist, use_container_width=True)

# Pesos
with st.expander("📊 Pesos utilizados pelo CLiNAP-G"):
    for var, peso in zip(variaveis_g, pesos_g):
        st.markdown(f"- **{var}**: `{peso:.4f}`")

# Legenda
with st.expander("📚 Legenda explicativa do painel"):
    st.markdown("""
    Este painel compara agrupamentos baseados em CLiNAP e CLiNAP-G:
    - **CLiNAP**: usa IMC e HbA1c com pesos manuais.
    - **CLiNAP-G**: versão avançada com IMC, HbA1c e Calorias, usando pesos aprendidos automaticamente via coesão + penalização por grafo.
    """)

# ---- Tabela final ----
st.markdown("### 🧾 Tabela com dados filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# ---- Exportações (agora abaixo da tabela) ----
import base64
import io
from xhtml2pdf import pisa

st.markdown("### 💾 Exportações")

# Exportar CSV
csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Baixar CSV com dados filtrados",
    data=csv,
    file_name="dados_filtrados.csv",
    mime="text/csv",
    key="csv_download_final"
)

# Exportar PDF com opções
with st.expander("📄 Exportar relatório em PDF"):
    opcoes_pdf = st.radio("Escolha o tipo de relatório:", ["Relatório individual", "Panorama geral"], key="tipo_pdf")

    if opcoes_pdf == "Relatório individual":
        if "paciente" in locals():
            def gerar_pdf_html_individual(p):
                return f"""
                <html><body>
                <h2>Relatório Individual - ID {p['ID']}</h2>
                <p><strong>Classificação:</strong> {p['Classificacao']}</p>
                <p><strong>Escore CLiNAP:</strong> {p['Escore_risco']} ({p['Escore_nivel']})</p>
                <p><strong>Escore CLiNAP-G:</strong> {'{:.1f}'.format(p['Escore_CLiNAP_G']) if not pd.isna(p['Escore_CLiNAP_G']) else 'N/A'}</p>
                <p><strong>IMC:</strong> {p['IMC']}  |  <strong>HbA1c:</strong> {p['HbA1c']}  |  <strong>Calorias:</strong> {p['Calorias']} kcal</p>
                </body></html>
                """

            def gerar_pdf_download(html):
                result = io.BytesIO()
                pisa.CreatePDF(io.StringIO(html), dest=result)
                return result.getvalue()

            html_ind = gerar_pdf_html_individual(paciente)
            pdf_ind = gerar_pdf_download(html_ind)
            b64 = base64.b64encode(pdf_ind).decode()
            href_ind = f'<a href="data:application/pdf;base64,{b64}" download="relatorio_paciente_{paciente["ID"]}.pdf">📄 Baixar PDF do paciente</a>'
            st.markdown(href_ind, unsafe_allow_html=True)
        else:
            st.info("Selecione um paciente para gerar o PDF individual.")

    elif opcoes_pdf == "Panorama geral":
        def gerar_pdf_html_geral():
            filtro1 = f"{f1}: {v1}" if v1 != "Todos" else "Todos"
            filtro2 = f"{f2}: {v2}" if v2 != "Todos" else "Todos"
            return f"""
            <html><body>
            <h2>Relatório Geral do Painel</h2>
            <p><strong>Filtros aplicados:</strong> {filtro1} | {filtro2}</p>
            <p><strong>Total de pacientes:</strong> {len(df_filtrado)}</p>
            <p><strong>Cluster:</strong> {cluster_coluna}</p>
            <p><strong>Média IMC:</strong> {df_filtrado['IMC'].mean():.2f} | <strong>Média HbA1c:</strong> {df_filtrado['HbA1c'].mean():.2f}</p>
            <p><strong>Escore médio CLiNAP:</strong> {df_filtrado['Escore_risco'].mean():.1f}</p>
            <p><strong>Escore médio CLiNAP-G:</strong> {df_filtrado['Escore_CLiNAP_G'].mean():.1f}</p>
            </body></html>
            """

        html_geral = gerar_pdf_html_geral()
        pdf_geral = gerar_pdf_download(html_geral)
        b64_geral = base64.b64encode(pdf_geral).decode()
        href_geral = f'<a href="data:application/pdf;base64,{b64_geral}" download="relatorio_geral.pdf">🖼️ Baixar PDF do cenário geral</a>'
        st.markdown(href_geral, unsafe_allow_html=True)
