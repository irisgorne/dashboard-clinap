 
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

# Salvar no diretório data
df.to_csv("data/base_simulada.csv", index=False)

print("✅ Base simulada salva em data/base_simulada.csv")
from src.preprocessamento import carregar_e_preprocessar

df_processado = carregar_e_preprocessar("data/base_simulada.csv")
print(df_processado.head())
from src.clinap import aplicar_clinap

# Seleciona apenas variáveis numéricas padronizadas
variaveis = ["IMC_zscore", "Calorias_zscore", "HbA1c_zscore", "Idade_zscore"]
X = df_processado[variaveis].values

# Aplica o CLiNAP
labels, pesos = aplicar_clinap(X, k=3)

# Exibe resultados
print("\n🔎 Clusters atribuídos:", labels)
print("\n📊 Pesos aprendidos para cada variável:", dict(zip(variaveis, pesos)))
from src.visualizacoes import plotar_clusters_pca, plotar_pesos

# Visualiza clusters em 2D com PCA
plotar_clusters_pca(X, labels, variaveis)

# Visualiza os pesos aprendidos
plotar_pesos(variaveis, pesos)

print("Salvando os gráficos...")

# Salva os gráficos
from src.visualizacoes import plotar_clusters_pca, plotar_pesos
plotar_clusters_pca(X, labels, variaveis)
plotar_pesos(variaveis, pesos)

print("Gráficos salvos em /outputs.")
