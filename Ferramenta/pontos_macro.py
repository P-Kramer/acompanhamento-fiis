import pandas as pd

# Tabela de decisão original
tabela_decisao = pd.DataFrame([
    # Direta
    {"inflexao_macro": "subiu", "dy_atual": "subiu", "tipo_correlacao": "direta", "sinal": "Comprar"},
    {"inflexao_macro": "subiu", "dy_atual": "caiu", "tipo_correlacao": "direta", "sinal": "Esperar"},
    {"inflexao_macro": "caiu", "dy_atual": "subiu", "tipo_correlacao": "direta", "sinal": "Vender"},
    {"inflexao_macro": "caiu", "dy_atual": "caiu", "tipo_correlacao": "direta", "sinal": "Neutro"},
    {"inflexao_macro": "estavel", "dy_atual": "subiu", "tipo_correlacao": "direta", "sinal": "Neutro"},
    {"inflexao_macro": "estavel", "dy_atual": "caiu", "tipo_correlacao": "direta", "sinal": "Neutro"},
    # Inversa
    {"inflexao_macro": "subiu", "dy_atual": "subiu", "tipo_correlacao": "inversa", "sinal": "Vender"},
    {"inflexao_macro": "subiu", "dy_atual": "caiu", "tipo_correlacao": "inversa", "sinal": "Vender"},
    {"inflexao_macro": "caiu", "dy_atual": "subiu", "tipo_correlacao": "inversa", "sinal": "Comprar"},
    {"inflexao_macro": "caiu", "dy_atual": "caiu", "tipo_correlacao": "inversa", "sinal": "Esperar"},
    {"inflexao_macro": "estavel", "dy_atual": "subiu", "tipo_correlacao": "inversa", "sinal": "Neutro"},
    {"inflexao_macro": "estavel", "dy_atual": "caiu", "tipo_correlacao": "inversa", "sinal": "Neutro"},
])

# Função para detectar inflexão em uma série (últimos 21 dias úteis)
def detectar_inflexao(serie, janela=21, limite=0.01):
    serie = serie.dropna()
    if len(serie) < janela:
        return "estavel"
    recente = serie.iloc[-janela:]
    delta = (recente.iloc[-1] - recente.iloc[0]) / abs(recente.iloc[0])
    if delta > limite:
        return "subiu"
    elif delta < -limite:
        return "caiu"
    else:
        return "estavel"

# Geração de sinais por fundo
def gerar_sinais_para_fundo(fundo_resultados, df_dy, df_macro, correlacoes_por_variavel, categoria, janela=21, limite=0.01):
    sinais = []
    for resultado in fundo_resultados:
        for fundo, df_res in resultado.items():
            for _, row in df_res.iterrows():
                variavel = row["Variável"]
                corr = row["Correlação"]
                tipo = correlacoes_por_variavel.get(variavel, {}).get(categoria)
                if tipo is None or variavel not in df_macro.columns or fundo not in df_dy.columns:
                    continue

                serie_macro = df_macro[variavel].dropna()
                inflexao = detectar_inflexao(serie_macro, janela, limite)

                serie_dy = df_dy[fundo].dropna()
                direcao_dy = detectar_inflexao(serie_dy, janela, limite)

                linha = tabela_decisao[
                    (tabela_decisao["inflexao_macro"] == inflexao) &
                    (tabela_decisao["dy_atual"] == direcao_dy) &
                    (tabela_decisao["tipo_correlacao"] == tipo)
                ]

                if not linha.empty:
                    sinais.append((linha.iloc[0]["sinal"], abs(corr)))
    return sinais

# Síntese final do sinal com ponderação
def sintetizar_sinal_final(sinais):
    if not sinais:
        return "Neutro"
    df_sinais = pd.DataFrame(sinais, columns=["sinal", "peso"])
    resultado = df_sinais.groupby("sinal")["peso"].sum().sort_values(ascending=False)
    return resultado.idxmax()


# Supondo que já estejam importados:
# df_dy_diario: DataFrame com DYs diários
# df_merged: variáveis macroeconômicas (também com base diária)
# resultados: lista de correlações por fundo
# correlacoes_por_variavel: tipo de correlação por variável e categoria

from alfas import df_dy_diario
from dados import df_merged
from corr import resultados
from dados import correlacoes_por_variavel

categoria = "Pós-fixado"
sinais_categoria = []

for resultado in resultados.get(categoria, []):
    for fundo, _ in resultado.items():
        sinais = gerar_sinais_para_fundo(
            [resultado],
            df_dy_diario,
            df_merged,
            correlacoes_por_variavel,
            categoria,
            janela=21,
            limite=0.01
        )
        decisao_final = sintetizar_sinal_final(sinais)
        sinais_categoria.append((fundo, decisao_final))

