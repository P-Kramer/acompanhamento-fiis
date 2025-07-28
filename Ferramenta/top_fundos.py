import pandas as pd

from alfas import alfas

# Leitura e preparação dos dados
alfas["Data"] = pd.to_datetime(alfas["Data"])
alfas = alfas.sort_values("Data", ascending=True).reset_index(drop=True)
janela = 21  # dias úteis para cálculo da consistência

# Remove a coluna "Data" para cálculos
df_alfa = alfas.drop(columns=["Data"])

# Aplica o cálculo de score de consistência (número de dias com alfa > 0 nos últimos 21 dias)
df_score_raw = df_alfa.rolling(window=janela).apply(lambda x: (x > 0).sum(), raw=True)

# Normaliza para nota de 0 a 10
df_score1 = (df_score_raw / janela * 10).clip(0, 10).round(2)

# Reinsere a coluna de datas correspondente
df_score1["Data"] = alfas["Data"]

# Define o limite como 1º de janeiro de 2017
data_limite = pd.Timestamp("2017-01-02")
ontem = df_score1["Data"].max()
df_score1 = df_score1[df_score1["Data"] >= data_limite].reset_index(drop=True)

import pandas as pd

# Define o limite de variação (0.3% ao dia como nota 10)
limite_2 = 0.003

# Garante que a coluna de data esteja ordenada
alfas["Data"] = pd.to_datetime(alfas["Data"])
alfas = alfas.sort_values("Data").reset_index(drop=True)

# Separa o alfa dos fundos
df_alfa = alfas.drop(columns=["Data"])

# Calcula as médias móveis
nota_5d  = df_alfa.rolling(window=5).mean().apply(lambda x: ((x + limite_2) / (2 * limite_2)) * 10)
nota_21d = df_alfa.rolling(window=21).mean().apply(lambda x: ((x + limite_2) / (2 * limite_2)) * 10)
nota_63d = df_alfa.rolling(window=63).mean().apply(lambda x: ((x + limite_2) / (2 * limite_2)) * 10)

# Pondera os scores conforme pesos definidos
df_score2 = (
    0.5 * nota_5d +
    0.3 * nota_21d +
    0.2 * nota_63d
).clip(lower=0, upper=10).round(2)

# Adiciona a coluna de datas
df_score2["Data"] = alfas["Data"]

data_limite = pd.Timestamp("2017-01-02")
df_score2 = df_score2[df_score2["Data"] >= data_limite].reset_index(drop=True)

import pandas as pd

# Define os parâmetros
limite_3 = 0.1  # 10% acumulado
dias_3 = 63     # Janela de 63 dias úteis

# Garante que a coluna de data esteja ordenada
alfas["Data"] = pd.to_datetime(alfas["Data"])
alfas = alfas.sort_values("Data").reset_index(drop=True)

# Separa os alfas
df_alfa = alfas.drop(columns=["Data"])

# Calcula o alfa acumulado por janela de 63 dias
acumulado = df_alfa.rolling(window=dias_3).sum()

# Converte para nota de 0 a 10 com base no limite
df_score3 = ((acumulado + limite_3) / (2 * limite_3)) * 10
df_score3 = df_score3.clip(lower=0, upper=10).round(2)

# Adiciona a coluna de datas
df_score3["Data"] = alfas["Data"]

data_limite = pd.Timestamp("2017-01-02")
df_score3 = df_score3[df_score3["Data"] >= data_limite].reset_index(drop=True)

import pandas as pd

# Define parâmetros
limite_4 = 0.025  # desvio padrão máximo tolerado (2.5%)
dias_4 = 126      # janela de cálculo da volatilidade

# Garante que a data esteja em ordem
alfas["Data"] = pd.to_datetime(alfas["Data"])
alfas = alfas.sort_values("Data").reset_index(drop=True)

# Remove coluna de data e separa os alfas
df_alfa = alfas.drop(columns=["Data"])

# Calcula o desvio padrão em janela móvel
desvios_movel = df_alfa.rolling(window=dias_4).std()

# Converte para nota de 0 a 10 (menor volatilidade => nota maior)
df_score4 = (1 - desvios_movel.clip(upper=limite_4) / limite_4) * 10
df_score4 = df_score4.clip(lower=0, upper=10).round(2)

# Adiciona a coluna "Data"
df_score4["Data"] = alfas["Data"]

data_limite = pd.Timestamp("2017-01-02")
df_score4 = df_score4[df_score4["Data"] >= data_limite].reset_index(drop=True)

# Define pesos utilizados
peso_1 = 0.30  # Consistência
peso_2 = 0.25  # Força
peso_3 = 0.25  # Acumulado
peso_4 = 0.20  # Volatilidade

dias = 5

# Seleciona os últimos dias úteis (com base em df_score1)
ultimos_dias = df_score1["Data"].tail(dias).tolist()

# Inicializa o DataFrame com a coluna Data
df_score_final = pd.DataFrame({"Data": ultimos_dias})

# Para cada fundo, calcula a média final ponderada dos últimos 5 dias
for fundo in df_score1.columns:
    if fundo == "Data":
        continue

    media_1 = df_score1[df_score1["Data"].isin(ultimos_dias)][fundo].mean()
    media_2 = df_score2[df_score2["Data"].isin(ultimos_dias)][fundo].mean()
    media_3 = df_score3[df_score3["Data"].isin(ultimos_dias)][fundo].mean()
    media_4 = df_score4[df_score4["Data"].isin(ultimos_dias)][fundo].mean()

    score_final = (
        peso_1 * media_1 +
        peso_2 * media_2 +
        peso_3 * media_3 +
        peso_4 * media_4
    )

    df_score_final[fundo] = [round(score_final, 2)] * dias  # mesmo valor para os dias selecionados (ou ajuste para apenas uma linha)

# Transforma em ranking final
df_ranking_final = df_score_final.drop(columns=["Data"]).mean().sort_values(ascending=False)
df_ranking_final = pd.DataFrame(df_ranking_final, columns=[f"Score_Final"])
df_ranking_final.reset_index(inplace=True)
df_ranking_final.columns = ["Fundo", f"Score_Final"]