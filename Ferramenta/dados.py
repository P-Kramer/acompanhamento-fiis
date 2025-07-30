import pandas as pd
import json
import urllib.request
from datetime import datetime
from functools import reduce
from alfas import arquivo

# Lê a aba "Variáveis"
df_variaveis = pd.read_excel(arquivo, sheet_name="Variaveis")

# Datas
hoje = datetime.today()
data_inicio = '02/01/2016'
data_fim = hoje.strftime('%d/%m/%Y')

# Inicializa lista de DataFrames
lista_dfs = []
correlacoes_por_variavel = {}

for _, row in df_variaveis.iterrows():
    nome = row['Variável']
    fonte = row['Fonte']
    codigo = int(float(row['Código'])) if pd.notna(row['Código']) else None
    transformacao = row.get('Transformação', None)
    freq = row['Frequência']

    # Correlações esperadas por categoria
    correlacoes_por_variavel[nome] = {
        "Pós-fixado": str(row.get("Pós-fixado", "")).strip().lower(),
        "Inflação": str(row.get("Inflação", "")).strip().lower(),
        "Tijolo": str(row.get("Tijolo", "")).strip().lower(),
        "Carrego": str(row.get("Carrego", "")).strip().lower(),
    }

    # URL da API do Bacen
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}"

    if fonte == "Bacen":

        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                data_json = json.loads(data)

            df_raw = pd.DataFrame(data_json)
            df_raw['Data'] = pd.to_datetime(df_raw['data'], format='%d/%m/%Y')
            df_raw[nome] = pd.to_numeric(df_raw['valor'], errors='coerce')
            df_raw = df_raw[['Data', nome]]

            # Ajuste de frequência: última observação do mês
            df_raw = df_raw.set_index('Data')
            df_proc = df_raw.resample('ME').last().dropna().reset_index()

            # Transformações
            if transformacao == 'Pct':
                df_proc[nome] = df_proc[nome].pct_change()
                df_proc = df_proc.dropna()
            elif transformacao == 'Diff':
                df_proc[nome] = df_proc[nome].diff()
                df_proc = df_proc.dropna()

            # Adiciona coluna MesAno
            df_proc["MesAno"] = df_proc["Data"].dt.strftime("%m/%Y")

            # Organiza colunas
            df_proc = df_proc.drop(columns=["Data"])
            df_proc = df_proc[["MesAno", nome]]

            lista_dfs.append(df_proc)

        except Exception as e:
            print(f"Erro ao processar {nome} ({codigo}): {e}")



import urllib.request
import pandas as pd
import io  # Para lidar com arquivos em memória

# URL do arquivo CSV com os dados do EPU para o Brasil
url = 'https://www.policyuncertainty.com/media/Brazil_Policy_Uncertainty_Data.csv'

# Baixar o conteúdo do arquivo diretamente na memória
response = urllib.request.urlopen(url)

csv_data = response.read().decode('utf-8')

# Ler os dados diretamente no pandas usando io.StringIO
df_epu = pd.read_csv(io.StringIO(csv_data))

# Filtrar apenas os dados a partir de 2016
df_epu = df_epu[df_epu['year'] >= 2016]

# Criar uma coluna de data real para ordenação
df_epu["Data"] = pd.to_datetime(dict(year=df_epu["year"], month=df_epu["month"], day=1))

# Renomear a coluna e calcular a variação percentual
df_epu = df_epu.rename(columns={"Brazil_Policy_Index": "EPU"})
df_epu["EPU"] = df_epu["EPU"].pct_change()

# Criar a coluna MesAno no formato "MM/YYYY"
df_epu["MesAno"] = df_epu["Data"].dt.strftime("%m/%Y")

# Reordenar usando a coluna de data e selecionar apenas as colunas finais
df_epu = df_epu.sort_values("Data")[["MesAno", "EPU"]].dropna().reset_index(drop=True)

lista_dfs.append(df_epu)

# Junta todos os DataFrames com base em MesAno
df_merged = reduce(lambda left, right: pd.merge(left, right, on="MesAno", how="outer"), lista_dfs)

# Ordena por MesAno
df_merged["MesAno"] = pd.to_datetime(df_merged["MesAno"], format="%m/%Y")
df_merged = df_merged.sort_values("MesAno").reset_index(drop=True)
df_merged["MesAno"] = df_merged["MesAno"].dt.strftime("%m/%Y")

# Agora você tem:
# df_merged → base com as variáveis macroeconômicas
# correlacoes_por_variavel → dicionário com a correlação esperada por categoria
