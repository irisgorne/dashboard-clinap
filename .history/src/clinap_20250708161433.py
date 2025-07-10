# src/clinap.py

import numpy as np
from sklearn.cluster import KMeans

def calcular_variancia_intra_cluster(X, labels, k):
    n_features = X.shape[1]
    variancia_total = np.zeros(n_features)

    for cluster in range(k):
        pontos = X[labels == cluster]
        if len(pontos) > 0:
            variancia_total += np.var(pontos, axis=0)
    return variancia_total

def aprender_pesos(X, labels, k):
    variancia = calcular_variancia_intra_cluster(X, labels, k)
    pesos = 1 / (variancia + 1e-6)  # Para evitar divisão por zero
    pesos = pesos / np.sum(pesos)  # Normaliza para somar 1
    return pesos

def aplicar_clinap(X, k=3, max_iter=10):
    # Inicializa com pesos iguais
    pesos = np.ones(X.shape[1]) / X.shape[1]

    for i in range(max_iter):
        # Aplica pesos nas variáveis
        X_ponderado = X * pesos

        # Aplica KMeans
        modelo = KMeans(n_clusters=k, random_state=42)
        labels = modelo.fit_predict(X_ponderado)

        # Atualiza os pesos
        novos_pesos = aprender_pesos(X, labels, k)

        # Convergência (opcional)
        if np.allclose(novos_pesos, pesos):
            break

        pesos = novos_pesos

    return labels, pesos
