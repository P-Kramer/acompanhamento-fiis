# Reimportar bibliotecas após reset
import pandas as pd
import numpy as np

from dados import df_merged
from alfas import df_dy_mensal
from Ferramenta.lista_fundos_analisados import estrategias_fiis_reorganizado
from dados import correlacoes_por_variavel


def calcular_correlacoes(
    df_variaveis: pd.DataFrame,
    df_dy: pd.DataFrame,
    estrategias_fiis_reorganizado: dict,
    correlacoes_esperadas: dict,
    janela_suavizacao: int = 6,
    min_periodos: int = 3,
    max_lag: int = 12,
    limite_correlacao: float = 0.3
) -> dict:
    resultados_por_categoria = {}

    df_dy = df_dy.copy()
    df_variaveis = df_variaveis.copy()

    # Garantir datas
    if df_dy.index.dtype == "object":
        df_dy.index = pd.to_datetime(df_dy.index, format="%m/%Y")
    if "MesAno" in df_variaveis.columns:
        df_variaveis["MesAno"] = pd.to_datetime(df_variaveis["MesAno"], format="%m/%Y")
        df_variaveis = df_variaveis.set_index("MesAno")
    elif df_variaveis.index.dtype == "object":
        df_variaveis.index = pd.to_datetime(df_variaveis.index, format="%m/%Y")

    todas_variaveis = df_variaveis.columns.tolist()

    for categoria, fundos in estrategias_fiis_reorganizado.items():
        resultado_categoria = []
        for fundo in fundos:
            if fundo not in df_dy.columns:
                continue

            lista_resultados_fundo = []

            for variavel in todas_variaveis:
                if variavel not in df_variaveis.columns:
                    continue

                direcao = correlacoes_esperadas.get(variavel, {}).get(categoria, None)
                if not direcao:
                    continue

                df = pd.DataFrame({
                    "DY": df_dy[fundo],
                    "Variavel": df_variaveis[variavel]
                }).dropna()

                # ➕ Aplicar diferença no DY para trabalhar com variação
                df["DY"] = df["DY"].diff()

                df["DY"] = df["DY"].rolling(window=janela_suavizacao, min_periods=min_periodos).mean()
                df["Variavel"] = df["Variavel"].rolling(window=janela_suavizacao, min_periods=min_periodos).mean()
                df = df.dropna()

                melhor_lag = None
                melhor_corr = None

                for lag in range(1, max_lag + 1):
                    df_lagged = df.copy()
                    df_lagged["Variavel_Lag"] = df_lagged["Variavel"].shift(lag)
                    df_lagged = df_lagged.dropna()

                    if len(df_lagged) <= 30:
                        continue

                    x = df_lagged["Variavel_Lag"].values
                    y = df_lagged["DY"].values

                    pesos = np.clip(np.abs(x), *np.percentile(np.abs(x), [10, 90]))
                    pesos /= pesos.sum()

                    mx, my = np.average(x, weights=pesos), np.average(y, weights=pesos)
                    cov = np.average((x - mx) * (y - my), weights=pesos)
                    std_x = np.sqrt(np.average((x - mx) ** 2, weights=pesos))
                    std_y = np.sqrt(np.average((y - my) ** 2, weights=pesos))

                    corr = cov / (std_x * std_y) if std_x > 0 and std_y > 0 else np.nan

                    if direcao == "direta" and corr > limite_correlacao:
                        if melhor_corr is None or abs(corr) > abs(melhor_corr):
                            melhor_corr = corr
                            melhor_lag = lag
                    elif direcao == "inversa" and corr < -limite_correlacao:
                        if melhor_corr is None or abs(corr) > abs(melhor_corr):
                            melhor_corr = corr
                            melhor_lag = lag

                if melhor_lag is not None:
                    lista_resultados_fundo.append({
                        "Variável": variavel,
                        "Defasagem": melhor_lag,
                        "Correlação": melhor_corr
                    })

            if lista_resultados_fundo:
                df_resultado_fundo = pd.DataFrame(lista_resultados_fundo)
                resultado_categoria.append({fundo: df_resultado_fundo})

        if resultado_categoria:
            resultados_por_categoria[categoria] = resultado_categoria

    return resultados_por_categoria


# Executar
resultados = calcular_correlacoes(
    df_variaveis=df_merged,
    df_dy=df_dy_mensal,
    estrategias_fiis_reorganizado=estrategias_fiis_reorganizado,
    correlacoes_esperadas=correlacoes_por_variavel,    janela_suavizacao = 6,
    min_periodos = 3,
    max_lag = 12,
    limite_correlacao = 0.3
)


for df in resultados["Tijolo"]:
    print(df)
