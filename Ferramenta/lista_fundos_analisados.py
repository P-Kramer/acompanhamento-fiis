import pandas as pd

# Caminho do arquivo
#arquivo = r"C:\Users\User\Documents\OneDrive\Documentos\Guilherme\Precos_Reuters.xlsm"
arquivo = r"C:\Users\User\Documents\OneDrive\Documentos\Guilherme\Precos_Reuters.xlsm"
# Abre apenas a aba "Preços"
df_precos = pd.read_excel(arquivo, sheet_name="Preços", header=None)

# Extrai os nomes dos fundos (linha 1) e categorias (linha 2) a partir da coluna C
fundos_raw = df_precos.iloc[0, 2:].dropna().tolist()  # linha 1 → nomes com .SA
categorias_raw = df_precos.iloc[1, 2:2+len(fundos_raw)].tolist()  # linha 2 → categorias

# Remove o sufixo ".SA" dos nomes dos fundos
nomes_fundos_limpos = [nome.replace(".SA", "") for nome in fundos_raw]

# Monta o dicionário {fundo: categoria}
estrategias_fiis = dict(zip(nomes_fundos_limpos, categorias_raw))

estrategias_fiis_reorganizado = {}

for fundo, categoria in estrategias_fiis.items():
    if categoria not in estrategias_fiis_reorganizado:
        estrategias_fiis_reorganizado[categoria] = []
    estrategias_fiis_reorganizado[categoria].append(fundo)

# (Opcional) Ordenar os tickers dentro de cada categoria
for fundos in estrategias_fiis_reorganizado.values():
    fundos.sort()