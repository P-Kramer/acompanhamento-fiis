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
df_epu["EPU"] = df_epu["EPU"].pct_change() * 100

# Criar a coluna MesAno no formato "MM/YYYY"
df_epu["MesAno"] = df_epu["Data"].dt.strftime("%m/%Y")

# Reordenar usando a coluna de data e selecionar apenas as colunas finais
df_epu = df_epu.sort_values("Data")[["MesAno", "EPU"]].dropna().reset_index(drop=True)


