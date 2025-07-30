import requests
from bs4 import BeautifulSoup
import pandas as pd

from lista_fundos_analisados import nomes_fundos_limpos
from alfas import wb
from alfas import precos

# Dicionário para armazenar os valores
valores_patrimoniais = {}

# Itera por todas as abas do arquivo
for sheet_name in wb.sheetnames:
    if sheet_name in nomes_fundos_limpos:
        try:
            ws = wb[sheet_name]
            valor = ws["N2"].value

            if valor is not None:
                # Converte para float, tratando vírgula como separador decimal se necessário
                valor_str = str(valor).replace(",", ".")
                valor_float = float(valor_str)
                valores_patrimoniais[sheet_name] = valor_float
            else:
                print(f"[{sheet_name}] Célula N2 vazia.")
        except Exception as e:
            print(f"[{sheet_name}] Erro ao ler N2: {e}")

from alfas import df_dy_diario

# Criar dicionário com os dados
dados_fiis = {}

for fundo, nav in valores_patrimoniais.items():
    dados_fiis[fundo] = {
        "PVP": precos[fundo].iloc[-1]/nav if fundo in precos else None,
        "Dividend_Yield": f'{round(df_dy_diario[fundo].iloc[-1]*100,2)}%'
    }

df_dados_fiis = pd.DataFrame.from_dict(dados_fiis, orient="index").reset_index().rename(columns={"index": "Fundo"})