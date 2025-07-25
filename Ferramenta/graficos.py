import matplotlib.pyplot as plt
import os
import pandas as pd

def gerar_graficos_dy_vs_cdi(
    df_dy: pd.DataFrame,
    serie_cdi: pd.Series,
    estrategias_fiis_reorganizado: dict,
    janela_suavizacao: int = 6,
    min_periodos: int = 3,
    pasta_saida: str = "Gráficos"
) -> dict:
    resultados = {}

    # Garante estrutura de pastas
    os.makedirs(pasta_saida, exist_ok=True)

    # Conversão de índice, se necessário
    df_dy = df_dy.copy()
    if df_dy.index.dtype == "object":
        df_dy.index = pd.to_datetime(df_dy.index, format="%m/%Y")

    if serie_cdi.index.dtype == "object":
        serie_cdi.index = pd.to_datetime(serie_cdi.index, format="%m/%Y")

    # CDI suavizado
    cdi_suavizado = serie_cdi.rolling(window=janela_suavizacao, min_periods=min_periodos).mean()

    for estrategia, fundos in estrategias_fiis_reorganizado.items():
        pasta_estrategia = os.path.join(pasta_saida, estrategia.replace("/", "-"))
        os.makedirs(pasta_estrategia, exist_ok=True)

        resultados[estrategia] = {}

        for fundo in fundos:
            if fundo not in df_dy.columns:
                continue

            # DY suavizado
            dy_suavizado = df_dy[fundo].rolling(window=janela_suavizacao, min_periods=min_periodos).mean()

            # Construir DataFrame combinado
            df_plot = pd.DataFrame({
                "DY": dy_suavizado,
                "CDI": cdi_suavizado
            }).dropna()

            if df_plot.empty:
                continue

            # Plot
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.set_title(f"{fundo} – DY vs CDI", fontsize=14)

            ax.plot(df_plot.index, df_plot["DY"], label=f"{fundo} – DY (6M)", color="blue", linewidth=2)
            ax.plot(df_plot.index, df_plot["CDI"], label="CDI (6M)", color="orange", linestyle="--", linewidth=2)

            ax.set_xlabel("Data")
            ax.set_ylabel("Taxa anualizada")
            ax.legend(loc="upper left", fontsize=9)
            plt.xticks(rotation=45)
            plt.tight_layout()

            caminho_arquivo = os.path.join(pasta_estrategia, f"{fundo}.png")
            fig.savefig(caminho_arquivo)
            plt.close(fig)

            resultados[estrategia][fundo] = fig

    return resultados

from alfas import df_dy_mensal
from Ferramenta.lista_fundos_analisados import estrategias_fiis_reorganizado
from alfas import serie_cdi

graficos = gerar_graficos_dy_vs_cdi(
    df_dy=df_dy_mensal,
    serie_cdi=serie_cdi,
    estrategias_fiis_reorganizado=estrategias_fiis_reorganizado
)

