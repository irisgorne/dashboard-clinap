# src/visualizacoes.py

import matplotlib
matplotlib.use('Agg')  # Evita problemas com ambientes sem interface gráfica

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np

def plotar_clusters_pca(X, labels, variaveis):
    pca = PCA(n_components=2)
    componentes = pca.fit_transform(X)

    df_plot = pd.DataFrame(componentes, columns=["PC1", "PC2"])
    df_plot["Cluster"] = labels

    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df_plot, x="PC1", y="PC2", hue="Cluster", palette="Set2", s=100)
    plt.title("Visualização dos Clusters com PCA")
    plt.xlabel("Componente Principal 1")
    plt.ylabel("Componente Principal 2")
    plt.legend(title="Cluster")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("outputs/cluster_pca.png")  # ✅ Salva o gráfico como imagem
    plt.close()

def plotar_pesos(variaveis, pesos):
    plt.figure(figsize=(8, 4))
    sns.barplot(x=variaveis, y=pesos, palette="viridis")
    plt.title("Importância das Variáveis (Pesos Aprendidos)")
    plt.ylabel("Peso Normalizado")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("outputs/cluster_pca.png")  # ✅ Salva o gráfico como imagem
    plt.close()
