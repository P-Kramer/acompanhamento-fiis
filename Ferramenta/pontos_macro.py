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

def detectar_inflexao_macro(serie,limite=0.01):
    serie = serie.dropna().sort_index()
    acumulado = serie.sum()
    print(serie)
    print(acumulado)
    print('-----------------')
    if acumulado > limite:
        return "subiu"
    elif acumulado < -limite:
        return "caiu"
    else:
        return "estavel"
def detectar_inflexao_dy(serie, janela=21, limite=0.01):
    serie = serie.dropna().sort_index()
    if len(serie) < janela:
        return "estavel"
    acumulado = serie.iloc[-janela:].sum()
    if acumulado > limite:
        return "subiu"
    elif acumulado < -limite:
        return "caiu"
    else:
        return "estavel"

from dateutil.relativedelta import relativedelta

def gerar_sinais_para_fundo(fundo_resultados, df_dy, df_macro, correlacoes_por_variavel, categoria, janela=21, limite=0.01):
    sinais = []
    for resultado in fundo_resultados:
        for fundo, df_res in resultado.items():
            for _, row in df_res.iterrows():
                variavel = row["Variável"]
                corr = row["Correlação"]
                lag = int(row["Defasagem"])
                tipo = correlacoes_por_variavel.get(variavel, {}).get(categoria)

                if tipo is None or variavel not in df_macro.columns or fundo not in df_dy.columns:
                    continue

                # Inflexão da variável macro (com defasagem em MESES)
                serie_macro = df_macro[["MesAno", variavel]].dropna()
                serie_macro["MesAno"] = pd.to_datetime(serie_macro["MesAno"], format="%m/%Y", errors="coerce")
                serie_macro.set_index("MesAno", inplace=True)
                serie_macro = serie_macro[variavel].sort_index()

                try:
                    ultima_data = serie_macro.index.max()
                    data_fim = ultima_data - relativedelta(months=lag)
                    data_inicio = data_fim - relativedelta(months=1)
                    trecho_macro = serie_macro.loc[data_inicio:data_fim]
                    #print(trecho_macro)
                    inflexao = detectar_inflexao_macro(trecho_macro, limite)
                except:
                    inflexao = "estavel"

                # Inflexão do DY atual (sem defasagem)
                serie_dy = df_dy[["Data", fundo]].dropna()
                serie_dy["Data"] = pd.to_datetime(serie_dy["Data"])
                serie_dy.set_index("Data", inplace=True)
                serie_dy = serie_dy[fundo].sort_index()

                try:
                    direcao_dy = detectar_inflexao_dy(serie_dy, janela, limite)
                except:
                    direcao_dy = "estavel"

                linha = tabela_decisao[
                    (tabela_decisao["inflexao_macro"] == inflexao) &
                    (tabela_decisao["dy_atual"] == direcao_dy) &
                    (tabela_decisao["tipo_correlacao"] == tipo)
                ]

                if not linha.empty:
                    sinais.append((linha.iloc[0]["sinal"], abs(corr)))
    return sinais

def sintetizar_sinal_final(sinais):
    if not sinais:
        return "Neutro"
    df_sinais = pd.DataFrame(sinais, columns=["sinal", "peso"])
    resultado = df_sinais.groupby("sinal")["peso"].sum().sort_values(ascending=False)
    return resultado.idxmax()

# Importações externas
from alfas import df_dy_diario
from dados import df_merged
from corr import resultados
from dados import correlacoes_por_variavel

# Pré-processamento do DY: diferenciar e manter coluna Data
var_df_dy_diario = df_dy_diario.copy()
for col in var_df_dy_diario.columns:
    if col != "Data":
        var_df_dy_diario[col] = var_df_dy_diario[col].diff()

# Execução para uma categoria
categoria = "Pós-fixado"
sinais_categoria = []

for resultado in resultados.get(categoria, []):
    for fundo, _ in resultado.items():
        sinais = gerar_sinais_para_fundo(
            [resultado],
            var_df_dy_diario,  # <- DY agora tratado com diff()
            df_merged,
            correlacoes_por_variavel,
            categoria,
            janela=21,
            limite=0.01
        )
        decisao_final = sintetizar_sinal_final(sinais)
        sinais_categoria.append((fundo, decisao_final))

print(f"Sinais para a categoria {categoria}")
print(sinais_categoria)
