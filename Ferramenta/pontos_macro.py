import pandas as pd
import numpy as np

# Simular uma matriz de decisão baseada na imagem fornecida
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

# Função para detectar inflexão
def detectar_inflexao(serie):
    if len(serie) < 3:
        return "estavel"
    delta = serie.iloc[-1] - serie.iloc[-3]
    if delta > 0.01:
        return "subiu"
    elif delta < -0.01:
        return "caiu"
    else:
        return "estavel"

# Função para gerar o sinal para cada fundo baseado em múltiplas variáveis
def gerar_sinais_para_fundo(fundo_resultados, df_dy, df_macro, correlacoes_por_variavel, categoria):
    sinais = []

    for resultado in fundo_resultados:
        for fundo, df_res in resultado.items():
            for _, row in df_res.iterrows():
                variavel = row["Variável"]
                corr = row["Correlação"]
                lag = row["Defasagem"]
                tipo = correlacoes_por_variavel.get(variavel, {}).get(categoria)

                if tipo is None:
                    continue

                # Identificar inflexão da variável macro
                serie_macro = df_macro[variavel].dropna().rolling(2).mean()
                inflexao = detectar_inflexao(serie_macro)

                # Identificar direção do DY
                serie_dy = df_dy[fundo].dropna().rolling(2).mean()
                direcao_dy = detectar_inflexao(serie_dy)

                # Procurar na matriz de decisão
                linha = tabela_decisao[
                    (tabela_decisao["inflexao_macro"] == inflexao) &
                    (tabela_decisao["dy_atual"] == direcao_dy) &
                    (tabela_decisao["tipo_correlacao"] == tipo)
                ]

                if not linha.empty:
                    sinais.append((linha.iloc[0]["sinal"], abs(corr)))

    return sinais

# Função agregadora final
def sintetizar_sinal_final(sinais):
    if not sinais:
        return "Neutro"
    df_sinais = pd.DataFrame(sinais, columns=["sinal", "peso"])
    resultado = df_sinais.groupby("sinal")["peso"].sum().sort_values(ascending=False)
    return resultado.idxmax()

from dados import df_merged
from alfas import df_dy_mensal
from corr import resultados
from dados import correlacoes_por_variavel

categoria = "Pós-fixado"
sinais_categoria = []

for resultado in resultados.get(categoria, []):
    for fundo, _ in resultado.items():
        sinais = gerar_sinais_para_fundo([resultado], df_dy_mensal, df_merged, correlacoes_por_variavel, categoria)
        decisao_final = sintetizar_sinal_final(sinais)
        sinais_categoria.append((fundo, decisao_final))

# Exibir os sinais
for fundo, decisao in sinais_categoria:
    print(f"{fundo}: {decisao}")


