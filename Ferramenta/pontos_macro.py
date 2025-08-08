import pandas as pd

# Tabela de decisão original
tabela_decisao = pd.DataFrame([
    # Correlação direta
    {"inflexao_macro": "subiu", "dy_atual": "subiu", "tipo_correlacao": "direta", "sinal": "Comprar"},
    {"inflexao_macro": "subiu", "dy_atual": "caiu", "tipo_correlacao": "direta", "sinal": "Comprar"},
    {"inflexao_macro": "subiu", "dy_atual": "estavel", "tipo_correlacao": "direta", "sinal": "Comprar"},

    {"inflexao_macro": "caiu", "dy_atual": "subiu", "tipo_correlacao": "direta", "sinal": "Vender"},
    {"inflexao_macro": "caiu", "dy_atual": "caiu", "tipo_correlacao": "direta", "sinal": "Vender"},
    {"inflexao_macro": "caiu", "dy_atual": "estavel", "tipo_correlacao": "direta", "sinal": "Vender"},

    {"inflexao_macro": "estavel", "dy_atual": "subiu", "tipo_correlacao": "direta", "sinal": "Neutro"},
    {"inflexao_macro": "estavel", "dy_atual": "caiu", "tipo_correlacao": "direta", "sinal": "Neutro"},
    {"inflexao_macro": "estavel", "dy_atual": "estavel", "tipo_correlacao": "direta", "sinal": "Neutro"},

    # Correlação inversa
    {"inflexao_macro": "subiu", "dy_atual": "subiu", "tipo_correlacao": "inversa", "sinal": "Vender"},
    {"inflexao_macro": "subiu", "dy_atual": "caiu", "tipo_correlacao": "inversa", "sinal": "Vender"},
    {"inflexao_macro": "subiu", "dy_atual": "estavel", "tipo_correlacao": "inversa", "sinal": "Vender"},

    {"inflexao_macro": "caiu", "dy_atual": "subiu", "tipo_correlacao": "inversa", "sinal": "Comprar"},
    {"inflexao_macro": "caiu", "dy_atual": "caiu", "tipo_correlacao": "inversa", "sinal": "Comprar"},
    {"inflexao_macro": "caiu", "dy_atual": "estavel", "tipo_correlacao": "inversa", "sinal": "Comprar"},

    {"inflexao_macro": "estavel", "dy_atual": "subiu", "tipo_correlacao": "inversa", "sinal": "Neutro"},
    {"inflexao_macro": "estavel", "dy_atual": "caiu", "tipo_correlacao": "inversa", "sinal": "Neutro"},
    {"inflexao_macro": "estavel", "dy_atual": "estavel", "tipo_correlacao": "inversa", "sinal": "Neutro"},
])


def detectar_inflexao_macro(serie, limite):
    """
    Detecta inflexão em uma série de variações já prontas.
    Se 'limite' não for fornecido, será calculado automaticamente via MAD.
    """
    serie = serie.dropna().sort_index()
    acumulado = serie.sum()

    if acumulado > limite:
        return "subiu"
    elif acumulado < -limite:
        return "caiu"
    else:
        return "estavel"

def detectar_inflexao_dy(serie, limite, janela=21):
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

def gerar_sinais_para_fundo(fundo_resultados, df_dy, df_macro, categoria, janela):
    sinais = []
    for resultado in fundo_resultados:
        for fundo, df_res in resultado.items():
            for _, row in df_res.iterrows():
                variavel = row["Variável"]
                corr = row["Correlação"]
                lag = int(row["Defasagem"])
                tipo = "direta" if corr >= 0 else "inversa"



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
                    limite_macro =(serie_macro - serie_macro.mean()).abs().mean()
                    inflexao = detectar_inflexao_macro(trecho_macro, limite_macro)
                except Exception as e:
                    inflexao = "estavel"


                # Inflexão do DY atual (sem defasagem)
                serie_dy = df_dy[["Data", fundo]].copy()
                serie_dy = serie_dy.dropna()
                serie_dy["Data"] = pd.to_datetime(serie_dy["Data"])
                serie_dy.set_index("Data", inplace=True)
                serie_dy = serie_dy[fundo].sort_index()

                limite_dy = (serie_dy - serie_dy.mean()).abs().mean()

                try:
                    direcao_dy = detectar_inflexao_dy(serie_dy, janela, limite_dy)
                except:
                    direcao_dy = "estavel"

                linha = tabela_decisao[
                    (tabela_decisao["inflexao_macro"] == inflexao) &
                    (tabela_decisao["dy_atual"] == direcao_dy) &
                    (tabela_decisao["tipo_correlacao"] == tipo)
                ]

                if linha.empty:
                    print(f"⚠️ Sem regra definida para: macro={inflexao}, DY={direcao_dy}, tipo={tipo}")

                else:
                    sinais.append((linha.iloc[0]["sinal"], abs(corr)))
    return sinais

def sintetizar_sinal_final(sinais):
    if not sinais:
        return "Neutro"
    df_sinais = pd.DataFrame(sinais, columns=["sinal", "peso"])
    resultado = df_sinais.groupby("sinal")["peso"].sum().sort_values(ascending=False)
    return resultado.idxmax()

import streamlit as st

df_dy_diario = st.session_state.get("df_dy_diario")
df_merged = st.session_state.get("df_merged")
resultados = st.session_state.get("resultados")

resultados = st.session_state.get("resultados")

if resultados is None:
    st.warning("⚠ A variável 'resultados' ainda não foi carregada.")
    st.stop()


# Pré-processamento do DY: diferenciar e manter coluna Data
var_df_dy_diario = df_dy_diario.copy()
for col in var_df_dy_diario.columns:
    if col != "Data":
        var_df_dy_diario[col] = var_df_dy_diario[col].diff()

# Execução para uma categoria
categorias = ["Pós-fixado", "Inflação", "Tijolo", "Carrego"]
sinais_categoria = []
for categoria in categorias:
    for resultado in resultados.get(categoria, []):
        for fundo, _ in resultado.items():
            sinais = gerar_sinais_para_fundo(
                [resultado],
                var_df_dy_diario,  # <- DY agora tratado com diff()
                df_merged,
                categoria,
                21,
            )
            decisao_final = sintetizar_sinal_final(sinais)
            sinais_categoria.append((fundo, decisao_final))


from dateutil.relativedelta import relativedelta
import pandas as pd

def analisar_variavel_macro(fundo, variavel, categoria, df_dy, df_macro, resultados, correlacoes_por_variavel, janela=21):
    # 1. Correlação e defasagem
    correlacao = None
    defasagem = None
    for resultado in resultados.get(categoria, []):
        if fundo in resultado:
            df_res = resultado[fundo]
            linha = df_res[df_res["Variável"] == variavel]
            if not linha.empty:
                correlacao = linha.iloc[0]["Correlação"]
                defasagem = int(linha.iloc[0]["Defasagem"])
                break

    if correlacao is None:
        print(f"⚠️ Nenhuma correlação entre {variavel} e {fundo} encontrada.")
        return

    tipo_correlacao = correlacoes_por_variavel.get(variavel, {}).get(categoria, "desconhecida")

    # 2. Série macro com defasagem
    serie_macro = df_macro[["MesAno", variavel]].dropna()
    serie_macro["MesAno"] = pd.to_datetime(serie_macro["MesAno"], format="%m/%Y", errors="coerce")
    serie_macro.set_index("MesAno", inplace=True)
    serie_macro = serie_macro[variavel].sort_index()

    ultima_data = serie_macro.index.max()
    data_fim = ultima_data - relativedelta(months=defasagem)
    data_inicio = data_fim - relativedelta(months=1)
    trecho_macro = serie_macro.loc[data_inicio:data_fim]

    limite_macro = (serie_macro - serie_macro.mean()).abs().mean()
    direcao_macro = detectar_inflexao_macro(trecho_macro, limite_macro)

    # 3. Série DY tratada
    serie_dy = df_dy[["Data", fundo]].dropna()
    serie_dy["Data"] = pd.to_datetime(serie_dy["Data"])
    serie_dy.set_index("Data", inplace=True)
    serie_dy = serie_dy[fundo].sort_index()
    serie_dy_diff = serie_dy.diff()
    limite_dy = (serie_dy_diff - serie_dy_diff.mean()).abs().mean()
    direcao_dy = detectar_inflexao_dy(serie_dy_diff, limite_dy, janela)

    # 4. Buscar sinal da tabela
    linha_sinal = tabela_decisao[
        (tabela_decisao["inflexao_macro"] == direcao_macro) &
        (tabela_decisao["dy_atual"] == direcao_dy) &
        (tabela_decisao["tipo_correlacao"] == tipo_correlacao)
    ]

    sinal = linha_sinal.iloc[0]["sinal"] if not linha_sinal.empty else "Neutro"

    # 5. Exibir
    print(f"📊 Análise para fundo: {fundo}")
    print(f"Variável macro: {variavel}")
    print(f"Correlação: {correlacao:.2f} | Tipo: {tipo_correlacao} | Defasagem: {defasagem} meses")
    print(f"Trecho macro considerado:\n{trecho_macro}")
    print(f"Inflexão macro detectada: {direcao_macro}")
    print(f"Inflexão DY detectada: {direcao_dy}")
    print(f"✅ Sinal sugerido: {sinal}")

"""print(analisar_variavel_macro(
    fundo="KNCR11",
    variavel="Selic",
    categoria="Pós-fixado",
    df_dy=var_df_dy_diario,
    df_macro=df_merged,
    resultados=resultados,
    correlacoes_por_variavel=correlacoes_por_variavel
))"""

st.session_state["sinais_categoria"] = sinais_categoria