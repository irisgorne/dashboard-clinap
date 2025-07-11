import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import StandardScaler

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
    pesos = 1 / (variancia + 1e-6)
    return pesos / np.sum(pesos)

def construir_grafo(X, threshold=0.6):
    dist_matrix = euclidean_distances(X)
    similarity_matrix = 1 / (1 + dist_matrix)
    grafo = {i: [] for i in range(len(X))}
    for i in range(len(X)):
        for j in range(i+1, len(X)):
            if similarity_matrix[i, j] > threshold:
                grafo[i].append(j)
                grafo[j].append(i)
    return grafo

def penalizacao_grafo(labels, grafo, lambda_):
    penalidade = 0
    for i, vizinhos in grafo.items():
        for j in vizinhos:
            if labels[i] != labels[j]:
                penalidade += 1
    return lambda_ * penalidade

def aplicar_clinap_g(X_original, k=3, max_iter=10, lambda_=0.5, threshold=0.6):
    """
    Implementa o CLiNAP-G com:
    - Padronização Z-score
    - Clusterização com pesos iterativos
    - Penalização com grafo de similaridade
    - Retorno de escore contínuo por paciente
    """
    scaler = StandardScaler()
    X = scaler.fit_transform(X_original)

    pesos = np.ones(X.shape[1]) / X.shape[1]
    grafo = construir_grafo(X, threshold=threshold)

    for _ in range(max_iter):
        X_ponderado = X * pesos
        modelo = KMeans(n_clusters=k, random_state=42)
        labels = modelo.fit_predict(X_ponderado)

        novos_pesos = aprender_pesos(X, labels, k)
        pesos = novos_pesos

    penalidade = penalizacao_grafo(labels, grafo, lambda_)

    # Escore contínuo individual
    escore_continuo = (X * pesos).sum(axis=1)

    return labels, pesos, penalidade, escore_continuo
