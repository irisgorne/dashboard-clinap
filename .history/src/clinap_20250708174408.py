# src/clinap.py

import numpy as np
from sklearn.cluster import KMeans

def calcular_variancia_intra_cluster(X, labels, k):
    """
    Calcula a variância intra-cluster para cada variável.
    Quanto menor a variância dentro do grupo, maior será o peso atribuído à variável.
    """
    n_features = X.shape[1]
    variancia_total = np.zeros(n_features)

    for cluster in range(k):
        pontos = X[labels == cluster]
        if len(pontos) > 0:
            variancia_total += np.var(pontos, axis=0)

    return variancia_total

def aprender_pesos(X, labels, k):
    """
    Aprende pesos adaptativos com base na variância intra-cluster.
    Quanto menor a variância, maior o peso.
    """
    variancia = calcular_variancia_intra_cluster(X, labels, k)
    pesos = 1 / (variancia + 1e-6)  # Adiciona um pequeno valor para evitar divisão por zero
    pesos /= np.sum(pesos)         # Normaliza os pesos (soma = 1)
    return pesos

def aplicar_clinap(X, k=3, max_iter=10):
    """
    Aplica o algoritmo CLiNAP:
    - Inicializa pesos iguais
    - Aplica KMeans com pesos
    - Atualiza pesos com base na coesão dos grupos
    - Repete até convergência ou número máximo de iterações
    """
    n_features = X.shape[1]
    pesos = np.ones(n_features) / n_features  # Pesos iniciais iguais

    for _ in range(max_iter):
        X_ponderado = X * pesos  # Aplica os pesos às variáveis

        modelo = KMeans(n_clusters=k, random_state=42)
        labels = modelo.fit_predict(X_ponderado)

        novos_pesos = aprender_pesos(X, labels, k)

        # Verifica convergência
        if np.allclose(novos_pesos, pesos):
            break

        pesos = novos_pesos

    return labels, pesos
