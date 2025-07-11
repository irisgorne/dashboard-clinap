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

# Cluster usado
st.sidebar.markdown("---")
cluster_coluna = st.sidebar.radio("🧠 Agrupamento:", ["Cluster_CLiNAP", "Cluster_CLiNAP_G"])
df_filtrado[cluster_coluna] = df_filtrado[cluster_coluna].astype(str)

# ---- Escore de risco e classificação ----
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

    # Filtro de escore na barra lateral
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Filtro por Escore de Risco")
    escore_min = st.sidebar.slider("Mostrar pacientes com escore igual ou maior que:", 0, 100, 0, step=5)
    df_filtrado = df_filtrado[df_filtrado["Escore_risco"] >= escore_min].sort_values("Escore_risco", ascending=False)


# Dispersão
st.markdown("### 🔁 Dispersão de IMC vs HbA1c")
fig = px.scatter(df_filtrado, x="IMC", y="HbA1c", color=cluster_coluna,
                 hover_data=["ID", "Sexo", "Idade", "Calorias", "Escore_risco"])
st.plotly_chart(fig, use_container_width=True)


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

# Gráfico comparativo
if "Escore_risco" in df_filtrado.columns and "Escore_CLiNAP_G" in df_filtrado.columns:
    st.markdown("### 📉 Comparativo: CLiNAP vs CLiNAP-G")
    fig_comp = px.scatter(df_filtrado, x="Escore_risco", y="Escore_CLiNAP_G", color=cluster_coluna,
                          trendline="ols", hover_data=["ID", "IMC", "HbA1c", "Calorias"])
    st.plotly_chart(fig_comp, use_container_width=True)

# Histograma
st.markdown("### 📊 Pacientes por Cluster")
hist = px.histogram(df_filtrado, x=cluster_coluna, color=cluster_coluna, text_auto=True)
st.plotly_chart(hist, use_container_width=True)

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

# Exportar CSV
csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button("📥 Baixar CSV", data=csv, file_name="dados_filtrados.csv", mime="text/csv")

# Exportar PDF
with st.expander("📄 Exportar relatório em PDF"):
    escolha = st.radio("Escolher tipo:", ["Relatório individual", "Panorama geral"])
    
    def gerar_pdf(html):
        buffer = io.BytesIO()
        pisa.CreatePDF(io.StringIO(html), dest=buffer)
        return buffer.getvalue()

    if escolha == "Relatório individual" and paciente is not None:
        html = f"""
        <html><body>
        <h2>Relatório - Paciente ID {paciente['ID']}</h2>
        <p><strong>Classificação:</strong> {paciente['Classificacao']}</p>
        <p><strong>IMC:</strong> {paciente['IMC']} | HbA1c: {paciente['HbA1c']} | Calorias: {paciente['Calorias']}</p>
        <p><strong>Escore CLiNAP:</strong> {paciente['Escore_risco']} ({paciente['Escore_nivel']})</p>
        <p><strong>Escore CLiNAP-G:</strong> {'{:.1f}'.format(paciente['Escore_CLiNAP_G'])}</p>
        </body></html>
        """
        pdf = gerar_pdf(html)
        b64 = base64.b64encode(pdf).decode()
        st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="paciente_{paciente["ID"]}.pdf">📄 Baixar PDF Individual</a>', unsafe_allow_html=True)

    elif escolha == "Panorama geral":
        html = f"""
        <html><body>
        <h2>Panorama Geral</h2>
        <p>Filtros: {f1}={v1} | {f2}={v2}</p>
        <p>Total: {len(df_filtrado)} pacientes</p>
        <p>Cluster: {cluster_coluna}</p>
        <p>Média IMC: {df_filtrado['IMC'].mean():.2f}</p>
        <p>Média HbA1c: {df_filtrado['HbA1c'].mean():.2f}</p>
        </body></html>
        """
        pdf = gerar_pdf(html)
        b64 = base64.b64encode(pdf).decode()
        st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="relatorio_geral.pdf">🖼️ Baixar PDF Geral</a>', unsafe_allow_html=True)
