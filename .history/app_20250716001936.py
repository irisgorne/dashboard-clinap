# app.py

import pandas as pd
import numpy as np
import os

from src.preprocessamento import carregar_e_preprocessar
from src.clinap import aplicar_clinap
from src.clinap_g import aplicar_clinap_g
from src.visualizacoes import plotar_clusters_pca, plotar_pesos

# 🔹 Garantir pastas
os.makedirs("data", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# 🔹 Gerar base simulada
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

# 🔹 Pré-processamento
X, variaveis = carregar_e_preprocessar("data/base_simulada.csv")

# 🔹 CLiNAP
labels_clinap, pesos_clinap = aplicar_clinap(X, k=3)
print("\n🔹 Clusters CLiNAP:", labels_clinap.tolist())
print("🔹 Pesos CLiNAP:", dict(zip(variaveis, pesos_clinap)))

# 🔹 CLiNAP-G
labels_g, pesos_g, penalidade_g, escore_g = aplicar_clinap_g(X, k=3)
print("\n🟢 Clusters CLiNAP-G:", labels_g.tolist())
print("🟢 Pesos CLiNAP-G:", dict(zip(variaveis, pesos_g)))

# 🔹 Gráficos
print("\n📊 Gerando gráficos...")

plotar_clusters_pca(X, labels_clinap, variaveis, nome_saida="cluster_pca_clinap.png")
plotar_pesos(variaveis, pesos_clinap, nome_saida="pesos_clinap.png")

plotar_clusters_pca(X, labels_g, variaveis, nome_saida="cluster_pca_clinapg.png")
plotar_pesos(variaveis, pesos_g, nome_saida="pesos_clinapg.png")

print("\n✅ Gráficos salvos em /outputs")

# 🔹 Base com rótulos de cluster
df_resultado = pd.read_csv("data/base_simulada.csv")
df_resultado["Cluster_CLiNAP"] = labels_clinap
df_resultado["Cluster_CLiNAP_G"] = labels_g
df_resultado.to_csv("data/base_resultado.csv", index=False)

print("📁 Arquivo final salvo como data/base_resultado.csv")