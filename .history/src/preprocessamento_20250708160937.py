# src/preprocessamento.py

import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

def carregar_e_preprocessar(caminho_csv):
    # Carrega os dados
    df = pd.read_csv(caminho_csv)

    # Codifica variáveis categóricas
    df["Sexo_cod"] = LabelEncoder().fit_transform(df["Sexo"])
    df["Região_cod"] = LabelEncoder().fit_transform(df["Região"])

    # Padroniza variáveis numéricas
    colunas_numericas = ["IMC", "Calorias", "HbA1c", "Idade"]
    scaler = StandardScaler()
    dados_padronizados = scaler.fit_transform(df[colunas_numericas])
    df_padronizado = pd.DataFrame(dados_padronizados, columns=[f"{c}_zscore" for c in colunas_numericas])

    # Junta tudo em um DataFrame final
    df_final = df_padronizado.copy()
    df_final["Sexo"] = df["Sexo_cod"]
    df_final["Região"] = df["Região_cod"]
    df_final["ID"] = df["ID"]

    return df_final
