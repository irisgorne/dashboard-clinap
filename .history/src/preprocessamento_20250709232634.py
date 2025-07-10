# src/preprocessamento.py

import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

def carregar_e_preprocessar(caminho_csv):
    df = pd.read_csv(caminho_csv)

    # Codifica variáveis categóricas
    df["Sexo_cod"] = LabelEncoder().fit_transform(df["Sexo"])
    df["Região_cod"] = LabelEncoder().fit_transform(df["Região"])

    # Padroniza variáveis numéricas
    colunas_numericas = ["IMC", "Calorias", "HbA1c", "Idade"]
    scaler = StandardScaler()
    dados_padronizados = scaler.fit_transform(df[colunas_numericas])

    # Cria novo DataFrame com zscores
    colunas_zscore = [f"{c}_zscore" for c in colunas_numericas]
    df_zscore = pd.DataFrame(dados_padronizados, columns=colunas_zscore)

    # Junta ao original
    df_final = pd.concat([df, df_zscore], axis=1)

    # Retorna a matriz de entrada (X) e os nomes das variáveis
    X = df_final[colunas_zscore].values
    return X, colunas_zscore
