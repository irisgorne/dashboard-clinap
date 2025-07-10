# src/preprocessamento.py

import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

def carregar_e_preprocessar(caminho_csv):
    # Carrega os dados
    df = pd.read_csv(caminho_csv)

    # Codifica variáveis categóricas, se existirem
    if "Sexo" in df.columns and "Região" in df.columns:
        df["Sexo_cod"] = LabelEncoder().fit_transform(df["Sexo"])
        df["Região_cod"] = LabelEncoder().fit_transform(df["Região"])
    else:
        df["Sexo_cod"] = 0
        df["Região_cod"] = 0

    # Define variáveis numéricas originais
    colunas_numericas = ["IMC", "Calorias", "HbA1c", "Idade"]

    # Padroniza variáveis numéricas
    scaler = StandardScaler()
    dados_padronizados = scaler.fit_transform(df[colunas_numericas])
    nomes_zscore = [f"{col}_zscore" for col in colunas_numericas]
    df_zscore = pd.DataFrame(dados_padronizados, columns=nomes_zscore)

    # Concatena outras variáveis ao dataframe
    df_zscore["Sexo"] = df["Sexo_cod"]
    df_zscore["Região"] = df["Região_cod"]
    df_zscore["ID"] = df["ID"]

    return df_zscore, nomes_zscore
