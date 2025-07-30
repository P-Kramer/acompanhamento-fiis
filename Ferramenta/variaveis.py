import pandas as pd
import json
import urllib.request
import requests
from datetime import datetime
from functools import reduce
import io


from alfas import arquivo
# === CONFIGURAÇÃO ===
ARQUIVO_EXCEL = arquivo  # Caminho do seu arquivo Excel
CLIENT_ID = "SEU_CLIENT_ID"       # Substitua pelo seu client_id da ANBIMA
CLIENT_SECRET = "SEU_CLIENT_SECRET"  # Substitua pelo seu client_secret da ANBIMA

# === GERAÇÃO AUTOMÁTICA DO TOKEN DA ANBIMA ===
def gerar_token_anbima(client_id, client_secret):
    url = "https://api.anbima.com.br/oauth2/token"
    payload = {"grant_type": "client_credentials"}
    response = requests.post(url, auth=(client_id, client_secret), data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Erro ao gerar token ANBIMA: {response.text}")

# === BACEN ===
def puxar_dado_bacen(codigo, nome_variavel, transformacao, freq, data_inicio, data_fim):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}"
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            data_json = json.loads(data)
        df_raw = pd.DataFrame(data_json)
        df_raw['Data'] = pd.to_datetime(df_raw['data'], format='%d/%m/%Y')
        df_raw[nome_variavel] = pd.to_numeric(df_raw['valor'], errors='coerce')
        df_raw = df_raw[['Data', nome_variavel]]

        if freq.lower().startswith('mensal'):
            df_raw = df_raw.set_index('Data').resample('ME').last().dropna().reset_index()
        elif freq.lower().startswith('trimestral'):
            df_raw = df_raw.set_index('Data').resample('Q').last().dropna().reset_index()
        else:
            df_raw = df_raw.dropna()

        if transformacao == 'Pct':
            df_raw[nome_variavel] = df_raw[nome_variavel].pct_change()
        elif transformacao == 'Diff':
            df_raw[nome_variavel] = df_raw[nome_variavel].diff()

        df_raw = df_raw.dropna()
        df_raw["MesAno"] = df_raw["Data"].dt.strftime("%m/%Y")
        return df_raw[["MesAno", nome_variavel]]
    except Exception as e:
        print(f"Erro ao puxar {nome_variavel} do Bacen: {e}")
        return None

# === EPU ===
def puxar_epu():
    url = 'https://www.policyuncertainty.com/media/Brazil_Policy_Uncertainty_Data.csv'
    try:
        response = urllib.request.urlopen(url)
        csv_data = response.read().decode('utf-8')
        df_epu = pd.read_csv(io.StringIO(csv_data))
        df_epu = df_epu[df_epu['year'] >= 2016]
        df_epu["Data"] = pd.to_datetime(dict(year=df_epu["year"], month=df_epu["month"], day=1))
        df_epu = df_epu.rename(columns={"Brazil_Policy_Index": "EPU"})
        df_epu["EPU"] = df_epu["EPU"].pct_change()
        df_epu["MesAno"] = df_epu["Data"].dt.strftime("%m/%Y")
        return df_epu.sort_values("Data")[["MesAno", "EPU"]].dropna().reset_index(drop=True)
    except Exception as e:
        print(f"Erro ao puxar EPU: {e}")
        return None

# === ANBIMA ===
def puxar_dado_anbima(endpoint, nome_variavel, token):
    try:
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        url = f"https://api.anbima.com.br/feed/indicadores/{endpoint}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Erro ao acessar {nome_variavel}: {response.status_code}")
            return None
        dados = response.json()
        registros = dados.get("data", dados)
        df = pd.DataFrame(registros)
        df["Data"] = pd.to_datetime(df["dataReferencia"])
        df[nome_variavel] = pd.to_numeric(df["valor"], errors="coerce")
        df["MesAno"] = df["Data"].dt.strftime("%m/%Y")
        return df.sort_values("Data")[["MesAno", nome_variavel]].dropna().reset_index(drop=True)
    except Exception as e:
        print(f"Erro ao puxar {nome_variavel} da ANBIMA: {e}")
        return None

# === EXECUÇÃO PRINCIPAL ===
hoje = datetime.today()
data_inicio = '02/01/2016'
data_fim = hoje.strftime('%d/%m/%Y')

df_variaveis = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Variaveis")
lista_dfs = []
correlacoes_por_variavel = {}

# Token ANBIMA só é gerado se necessário
usar_anbima = "Anbima" in df_variaveis['Fonte'].values
token_anbima = gerar_token_anbima(CLIENT_ID, CLIENT_SECRET) if usar_anbima else None

for _, row in df_variaveis.iterrows():
    nome = row['Variável']
    fonte = row['Fonte']
    codigo = str(row['Código']).strip()
    transformacao = row.get('Transformação', None)
    freq = row['Frequência']
    correlacoes_por_variavel[nome] = {
        "Pós-fixado": str(row.get("Pós-fixado", "")).strip().lower(),
        "Inflação": str(row.get("Inflação", "")).strip().lower(),
        "Tijolo": str(row.get("Tijolo", "")).strip().lower(),
        "Carrego": str(row.get("Carrego", "")).strip().lower(),
    }

    if fonte == "Bacen":
        df = puxar_dado_bacen(codigo, nome, transformacao, freq, data_inicio, data_fim)
    elif fonte == "Anbima":
        df = puxar_dado_anbima(codigo, nome, token_anbima)
    elif fonte == "Outro" and nome == "EPU":
        df = puxar_epu()
    else:
        print(f"Fonte desconhecida ou variável não suportada: {nome}")
        df = None

    if df is not None:
        lista_dfs.append(df)

# Junta tudo
df_merged = reduce(lambda left, right: pd.merge(left, right, on="MesAno", how="outer"), lista_dfs)
df_merged["MesAno"] = pd.to_datetime(df_merged["MesAno"], format="%m/%Y")
df_merged = df_merged.sort_values("MesAno").reset_index(drop=True)
df_merged["MesAno"] = df_merged["MesAno"].dt.strftime("%m/%Y")

# Pronto: você tem a base final
print(df_merged.head())
