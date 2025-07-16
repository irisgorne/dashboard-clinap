# =============================================================
# CLiNAP-G – OBSERVAÇÃO SOBRE EMBEDDING VIA GRAFO
# =============================================================

"""
A implementação atual do CLiNAP-G inclui:

- Padronização Z-score dos dados;
- Clusterização com pesos adaptativos aprendidos iterativamente;
- Penalização via grafo binário de similaridade, aplicada aos rótulos (labels) dos clusters.

Entretanto, ainda **não há implementação explícita de uma função de embedding não linear f(x_i)**, 
que projete os dados em um espaço latente estruturado com base no grafo.

Essa função embedding pode ser incorporada futuramente ao modelo, permitindo a extensão 
da função objetivo com o termo:

    γ * Σ_{i,j} A_ij * || f(x_i) - f(x_j) ||²

Onde:
- A_ij é a matriz de adjacência do grafo de similaridade;
- f(x_i) representa a projeção/embedding do indivíduo i;
- γ é um hiperparâmetro de regularização topológica.

Para estimar f(x_i), podem ser utilizados métodos como:
- SpectralEmbedding (Laplacian Eigenmaps)
- UMAP (Uniform Manifold Approximation and Projection)

A vantagem deste termo é permitir que pontos conectados no grafo
tenham representações próximas, mesmo em espaços não lineares ou de alta dimensão.

IMPORTANTE: A ausência atual do embedding explícito não compromete 
a validade nem a inovação metodológica da abordagem CLiNAP-G,
uma vez que a penalização topológica por rótulos já atua como regularização baseada em estrutura.

Esta etapa pode ser incorporada como **melhoria futura**, caso a complexidade dos dados assim o exija.
"""
ss