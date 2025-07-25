import pandas as pd
from datetime import datetime, timedelta
import urllib.request
import json
import numpy as np


from Ferramenta.lista_fundos_analisados import df_precos
from Ferramenta.lista_fundos_analisados import fundos_raw
from Ferramenta.lista_fundos_analisados import nomes_fundos_limpos


# (Opcional) Verificação
#print(dicionario_fundos_categorias)

# Extrai os preços a partir da linha 7 (linha 6 no índice zero)
precos = df_precos.iloc[6:, 1:2+len(fundos_raw)].copy()  # Coluna B (datas) + colunas dos fundos

# Ajusta os nomes das colunas
precos.columns = ["Data"] + nomes_fundos_limpos

# Converte coluna "Data" para datetime
precos["Data"] = pd.to_datetime(precos["Data"], format="%d/%m/%Y", errors="coerce")

# Remove linhas sem data
precos = precos.dropna(subset=["Data"])

# Ordena da data mais antiga para a mais recente
precos = precos.sort_values("Data").reset_index(drop=True)

# Filtra para manter apenas datas até o dia anterior
from datetime import datetime, timedelta
ontem = datetime.now().date() - timedelta(days=1)
precos = precos[precos["Data"].dt.date <= ontem].reset_index(drop=True)

# Definindo as datas dinâmicas
hoje = datetime.today()

data_inicio = '02/01/2017'
data_fim = hoje.strftime('%d/%m/%Y')

# URL da API do Banco Central para a série temporal do CDI (código 12)
url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}"

with urllib.request.urlopen(url) as response:
    data = response.read()
    data_json = json.loads(data)

    # Convertendo para DataFrame do pandas
    df_cdi = pd.DataFrame(data_json)

    # Convertendo as colunas para os tipos corretos
    df_cdi['data'] = pd.to_datetime(df_cdi['data'], format='%d/%m/%Y')
    df_cdi['valor'] = pd.to_numeric(df_cdi['valor'])
    df_cdi.columns = ['Data', 'Fator diário do CDI']

    # Substituindo a coluna com o novo fator bruto
    df_cdi['Fator diário do CDI'] = 1 + (df_cdi['Fator diário do CDI'] / 100)
    df_cdi["Taxa anual"]= df_cdi["Fator diário do CDI"]**(252)-1

# Unir os dois DataFrames pela coluna 'Data'
df_merged = pd.merge(precos, df_cdi, on="Data", how="inner")

# Inicializar DataFrame dos alfas
alfas = pd.DataFrame()
alfas["Data"] = df_merged["Data"]



# Calcular alfa para cada fundo
for fundo in precos.columns[1:]:
    preco_hoje = df_merged[fundo]
    preco_ontem = df_merged[fundo].shift(1)
    fator_cdi = df_merged['Fator diário do CDI']

    alfa = (preco_hoje / (preco_ontem * fator_cdi)) - 1
    alfas[fundo] = alfa

ontem = alfas["Data"].max()
alfas = alfas[alfas["Data"] < ontem].reset_index(drop=True)

mask = (alfas['Data'] >= '2020-03-01') & (alfas['Data'] <= '2021-12-01')
alfas = alfas[~mask]

import requests
from bs4 import BeautifulSoup



# Função para puxar P/VP e Dividend Yield do Status Invest
def get_pvp_e_dy(fii_ticker):
    url = f"https://statusinvest.com.br/fundos-imobiliarios/{fii_ticker.lower()}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    pvp = None
    dy = None

    indicadores = soup.select("div.top-info div.info")
    for indicador in indicadores:
        titulo = indicador.select_one("h3")
        valor = indicador.select_one("strong")

        if not titulo or not valor:
            continue

        titulo_text = titulo.text.strip()
        valor_text = valor.text.strip().replace(",", ".").replace("%", "")

        if "P/VP" in titulo_text:
            try:
                pvp = float(valor_text)
            except:
                pass
        elif "Dividend Yield" in titulo_text:
            try:
                dy = float(valor_text) / 100
            except:
                pass

    return pvp, dy

# Criar dicionário com os dados
dados_fiis = {}

fundos = []

for fundo in alfas.columns:
    if fundo != "Data":
        fundos.append(fundo)

for fundo in fundos:
    pvp, dy = get_pvp_e_dy(fundo)
    dados_fiis[fundo] = {
        "PVP": pvp,
        "Dividend_Yield": f'{round(dy*100,2)}%'
    }

df_dados_fiis = pd.DataFrame.from_dict(dados_fiis, orient="index").reset_index().rename(columns={"index": "Fundo"})

import pandas as pd
from datetime import datetime

# Lê o Excel com todas as abas de uma vez
arquivo = r"C:\Users\User\Documents\OneDrive\Documentos\Guilherme\Precos_Reuters.xlsm"
abas = pd.read_excel(arquivo, sheet_name=None)

import pandas as pd

# precos: seu DataFrame já existente com preços
precos["Data"] = pd.to_datetime(precos["Data"])  # Garante formato de data

# Lista para armazenar DYs
lista_dy = []

for nome_fundo, aba in abas.items():
    if nome_fundo == "Preços":
        continue  # pula a aba de preços
    if nome_fundo == "Variaveis":
        continue
    try:
        # Colunas B (data) e C (dividendo)
        df_div = aba.iloc[1:, [1, 2]].copy()
        df_div.columns = ["Data", "Dividendo"]
        df_div["Data"] = pd.to_datetime(df_div["Data"], errors="coerce")
        df_div["Dividendo"] = pd.to_numeric(df_div["Dividendo"], errors="coerce")
        df_div = df_div.dropna()

        # Merge com precos
        df_fundo_precos = precos[["Data", nome_fundo]].dropna()
        df_merged = pd.merge(df_div, df_fundo_precos, on="Data", how="inner")
        df_merged = df_merged.rename(columns={nome_fundo: "Preco"})

        # Calcula o DY anualizado
        df_merged["DY"] = (df_merged["Dividendo"] * 12) / df_merged["Preco"]
        df_merged["MesAno"] = df_merged["Data"].dt.strftime("%m/%Y")
        df_merged["Fundo"] = nome_fundo

        lista_dy.append(df_merged[["MesAno", "Fundo", "DY"]])
    
    except Exception as e:
        print(f"Erro ao processar {nome_fundo}: {e}")

# Concatena os DYs de todos os fundos
df_dy_historico = pd.concat(lista_dy, ignore_index=True)

# Constrói DataFrame final com índice MesAno e colunas dos fundos
df_dy_mensal = df_dy_historico.pivot_table(
    index="MesAno",
    columns="Fundo",
    values="DY",
    aggfunc="mean"
).sort_index()

# Garante que o índice esteja em formato datetime para ordenação
df_dy_mensal.index = pd.to_datetime(df_dy_mensal.index, format="%m/%Y")

# Ordena cronologicamente
df_dy_mensal = df_dy_mensal.sort_index()

# Aplica o ffill apenas a partir do primeiro valor não nulo de cada fundo
for coluna in df_dy_mensal.columns:
    primeira_data = df_dy_mensal[coluna].first_valid_index()
    if primeira_data is not None:
        mask = df_dy_mensal.index >= primeira_data
        df_dy_mensal.loc[mask, coluna] = df_dy_mensal.loc[mask, coluna].ffill()

# (opcional) Reconverte o índice para "mm/yyyy" se quiser visualizar assim
df_dy_mensal.index = df_dy_mensal.index.strftime("%m/%Y")

# 2. Atualiza a última linha de cada fundo com o DY vindo de dados_fiis
ultima_data = df_dy_mensal.index[-1]  # já está em formato string "mm/yyyy"

for fundo in df_dy_mensal.columns:
    if fundo in dados_fiis:
        dy_str = dados_fiis[fundo].get("Dividend_Yield")
        if dy_str and isinstance(dy_str, str) and dy_str.endswith('%'):
            try:
                dy = float(dy_str.replace('%', '').replace(',', '.')) / 100
                df_dy_mensal.loc[ultima_data, fundo] = dy
            except ValueError:
                print(f"Não foi possível converter o DY de {fundo}: {dy_str}")

# Arredonda todas as colunas exceto "MesAno"
colunas_para_arredondar = df_dy_mensal.columns.difference(["MesAno"])

df_dy_mensal[colunas_para_arredondar] = df_dy_mensal[colunas_para_arredondar].apply(
    pd.to_numeric, errors="coerce"
).round(4)

# Abertura já feita antes:
# abas = pd.read_excel(arquivo, sheet_name=None)

from openpyxl import load_workbook

wb = load_workbook(arquivo, data_only=True)

for nome_fundo in df_dy_mensal.columns:
    if nome_fundo not in wb.sheetnames or nome_fundo == "Preços":
        continue

    ws = wb[nome_fundo]
    datas_desdobramento = []

    for row in ws.iter_rows(min_row=2, min_col=8, max_col=8):
        cell = row[0].value
        if isinstance(cell, (datetime, pd.Timestamp)):
            datas_desdobramento.append(pd.to_datetime(cell))

    # Ajusta df_dy_mensal para cada data
    for data_desdobramento in datas_desdobramento:
        indices_anteriores = df_dy_mensal.index[
            pd.to_datetime(df_dy_mensal.index, format="%m/%Y") < data_desdobramento
        ]

        df_dy_mensal.loc[indices_anteriores, nome_fundo] = (
            df_dy_mensal.loc[indices_anteriores, nome_fundo] / 10
        )

df_dy_mensal.index = pd.to_datetime(df_dy_mensal.index, format="%m/%Y")
df_dy_mensal = df_dy_mensal.sort_index()

df_dy_mensal.index = pd.to_datetime(df_dy_mensal.index, format="%m/%Y")

# Parte 1 – Preparar df_cdi_mensal
df_cdi_mensal = df_cdi.copy()
df_cdi_mensal["Data"] = pd.to_datetime(df_cdi_mensal["Data"], errors="coerce")
df_cdi_mensal["Taxa anual"] = pd.to_numeric(df_cdi_mensal["Taxa anual"], errors="coerce")

# Agrupamento mensal
df_cdi_mensal["MesAno"] = df_cdi_mensal["Data"].dt.to_period("M").dt.to_timestamp()
df_cdi_mensal = df_cdi_mensal.groupby("MesAno")["Taxa anual"].last().reset_index()

# Definir índice como datetime (obrigatório para .rolling funcionar corretamente)
df_cdi_mensal = df_cdi_mensal.set_index("MesAno")
serie_cdi = df_cdi_mensal["Taxa anual"]