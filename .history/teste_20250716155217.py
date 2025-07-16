import pandas as pd

df = pd.read_csv("data/base_simulada.csv")

print("Colunas disponíveis no CSV:")
print(df.columns)  # Mostra o nome de todas as colunas

# Agora, veja os valores únicos de todas as colunas do tipo 'object'
for col in df.columns:
    if df[col].dtype == 'object':
        print(f"\nValores únicos em '{col}':")
        print(df[col].unique())
