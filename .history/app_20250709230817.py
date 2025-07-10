# app.py

import pandas as pd
import numpy as np
import os

# Criar pasta "data" se não existir
os.makedirs("data", exist_ok=True)

# Gerar base simulada
np.random.seed(42)

df = pd.DataFrame({
    "ID": range(1, 31),
    "IMC": np.round(np.random.normal(27, 4, 30), 1),
    "Calorias": np.round(np.random.normal(2200, 500, 30), 0),
    "HbA1c": np.round(np.random.normal(6.0, 1.2, 30), 2),
    "Idade": np.random.randint(18, 70, 30),
    "Sexo": np.random.choice(["Feminino", "Masculino"], 30),
    "Região": np.random.choice(["Norte", "Sul", "Leste", "Oeste"], 30)
})
df.to_csv("data/base_simulada.csv", index=False)
print("✅ Base simulada salva em data/base_simulada.csv")

# Pré-processamento
from src.preprocessamento import carregar_e_preprocessar
df_proc = carregar_e_preprocessar("data/base_simulada.csv")

# Seleciona variáveis zscore
variaveis = [col for col in df_proc.columns if col.endswith("_zscore")]
X = df_proc[variaveis].values

# === CLiNAP ===
from src.clinap import aplicar_clinap
labels_clinap, pesos_clinap = aplicar_clinap(X, k=3)
print("\n🔎 CLiNAP - Clusters:", labels_clinap)
print("📊 CLiNAP - Pesos:", dict(zip(variaveis, pesos_clinap)))

# === CLiNAP-G ===
from src.clinap_g import aplicar_clinap_g
labels_g, pesos_g, penalidade = aplicar_clinap_g(X, k=3, lambda_=0.7, threshold=0.6)
print("\n🔎 CLiNAP-G - Clusters:", labels_g)
print("📊 CLiNAP-G - Pesos:", dict(zip(variaveis, pesos_g)))
print(f"⚙️ Penalização por discordância no grafo: {penalidade:.2f}")

# Visualização
from src.visualizacoes import plotar_clusters_pca, plotar_pesos

print("\n🎨 Gerando gráficos...")

# CLiNAP
plotar_clusters_pca(X, labels_clinap, variaveis, nome_saida="cluster_pca_clinap.png")
plotar_pesos(variaveis, pesos_clinap, nome_saida="pesos_clinap.png")

# CLiNAP-G
plotar_clusters_pca(X, labels_g, variaveis, nome_saida="cluster_pca_clinapg.png")
plotar_pesos(variaveis, pesos_g, nome_saida="pesos_clinapg.png")

print("\n📁 Gráficos salvos em /outputs")
