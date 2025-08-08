import streamlit as st
import pandas as pd
import os
from PIL import Image
from glob import glob
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from pontos_macro import gerar_sinais_para_fundo, sintetizar_sinal_final


resultados = st.session_state.get("resultados")
correlacoes_por_variavel = st.session_state.get("correlacoes_por_variavel")
df_merged = st.session_state.get("df_merged")
df_dy_diario = st.session_state.get("df_dy_diario")
df_dy_mensal = st.session_state.get("df_dy_mensal")
serie_cdi = st.session_state.get("serie_cdi")
resultados_teses_quant = st.session_state.get("resultados_teses_quant")
ranking_antigo = st.session_state.get("ranking_antigo")
ranking_atual = st.session_state.get("ranking_atual")
sinais_categoria = st.session_state.get("sinais_categoria")
df_resultado = st.session_state.get("df_resultado")
df_ranking_final = st.session_state.get("df_ranking_final")
df_score1 = st.session_state.get("df_score1")
df_score2 = st.session_state.get("df_score2")
df_score3 = st.session_state.get("df_score3")
df_score4 = st.session_state.get("df_score4")

required_keys = ["df_score1", "df_score2", "df_score3", "df_score4", "df_ranking_final"]

if not all(k in st.session_state and st.session_state[k] is not None for k in required_keys):
    st.error("❌ Erro: Os dados de score ainda não foram carregados corretamente. Certifique-se de ter rodado o cálculo de alfas.")
    st.stop()


df_resultado = st.session_state.get("df_resultado")
if df_resultado is None:
    st.error("❌ Erro: O DataFrame `df_resultado` ainda não foi carregado. Verifique se o cálculo dos resultados quantitativos foi feito.")
    st.stop()


if df_ranking_final is None:
    st.warning("⚠ Dados de DY mensal ou CDI ainda não foram carregados.")
    st.stop()


estrategias_fiis_reorganizado = st.session_state.get("estrategias_fiis_reorganizado")
resultados_teses_macro = [{"Fundo": fundo, "Sinal": sinal.strip().capitalize()} for fundo, sinal in sinais_categoria]

def pagina_resultados():
    df_dy_mensal = st.session_state.get("df_dy_mensal")
    resultados = st.session_state.get("resultados")
    
    resultados_teses_quant = st.session_state.get("resultados_teses_quant") or []
    st.write("📦 DEBUG", st.session_state.get("correlacoes_por_variavel"))

    if not st.session_state.get("arquivo", False):
        st.warning("⚠ Por favor, carregue o arquivo na Página Inicial antes de continuar.")
        st.stop()
    st.set_page_config("\U0001F4CA Sinais e Análises", layout="wide")
    st.title("\U0001F4CA Sinais e Análises por Fundo")

    # Filtros combináveis
    st.subheader("\U0001F50E Filtros")
    col1, col2 = st.columns(2)

    with col1:
        categorias = list(estrategias_fiis_reorganizado.keys())
        categoria = st.selectbox("Categoria", ["Todas"] + categorias)
        limite_ranking = st.slider("Ranking máximo", 1, len(df_ranking_final), 20)

    with col2:
        sinais_macro = st.multiselect("Sinal Macroeconômico", ["Comprar", "Neutro", "Vender"])
        sinais_quant = st.multiselect("Sinal Quantitativo", ["Comprar", "Neutro", "Vender"])


    # Corrigir a ordenação real por Score_Final
    df_ordenado = df_ranking_final.sort_values("Score_Final", ascending=False).reset_index(drop=True)
    df_ordenado["Ranking"] = df_ordenado.index + 1

    # Aplica os filtros de forma sequencial com DataFrame
    df_filtrado = df_ordenado[df_ordenado["Ranking"] <= limite_ranking].copy()

    if categoria != "Todas":
        fundos_categoria = estrategias_fiis_reorganizado.get(categoria, [])
        df_filtrado = df_filtrado[df_filtrado["Fundo"].isin(fundos_categoria)]

    if sinais_macro:
        fundos_macro = [item["Fundo"] for item in resultados_teses_macro if item["Sinal"] in sinais_macro]
        df_filtrado = df_filtrado[df_filtrado["Fundo"].isin(fundos_macro)]


    if sinais_quant:
        fundos_quant = df_resultado[df_resultado["Sinal"].isin(sinais_quant)]["Fundo"].tolist()
        df_filtrado = df_filtrado[df_filtrado["Fundo"].isin(fundos_quant)]

    nome_fundos = st.multiselect(
    "🔍 Buscar fundo(s) pelo nome (opcional)",
    options=sorted(df_filtrado["Fundo"].tolist()),
    help="Você pode selecionar mais de um fundo digitando o nome ou parte dele"
)

    criterio_ordenacao = st.radio(
    "📊 Ordenar fundos por:",
    options=["Ranking", "Ordem alfabética"],
    horizontal=True
)

    aplicar_filtros = st.button("Aplicar Filtros")

    if not aplicar_filtros:
        st.stop()

    if criterio_ordenacao == "Ranking":
        # Já está ordenado por Score_Final
        fundos_filtrados = df_filtrado["Fundo"].tolist()
    else:
        fundos_filtrados = sorted(df_filtrado["Fundo"].tolist())


    if nome_fundos:
        fundos_filtrados = [f for f in fundos_filtrados if f in nome_fundos]


    for fundo in fundos_filtrados:
        # Encontra o df_corr correspondente ao fundo
        df_corr = None
        for resultado_categoria in resultados.values():
            for resultado in resultado_categoria:
                if fundo in resultado:
                    df_corr = resultado[fundo]
                    break
            if df_corr is not None:
                break

        if df_corr is None:
            continue  # pula se não encontrou o fundo nos resultados

    # ... restante do código segue aqui como está ...



        col1, col2 = st.columns([4, 1])
        # Determina posição atual e anterior
        pos_atual = ranking_atual.get(fundo)
        pos_antiga = ranking_antigo.get(fundo)

        with col1:
            if pos_atual is not None and pos_antiga is not None:
                delta = pos_antiga - pos_atual

                if delta > 0:
                    cor = "green"
                    simbolo = "▲"
                    texto_delta = f"+{delta}"
                elif delta < 0:
                    cor = "red"
                    simbolo = "▼"
                    texto_delta = f"{delta}"
                else:
                    cor = "black"
                    simbolo = "—"
                    texto_delta = ""

                ranking_info = f"# {pos_atual} <span style='color:{cor};'>{simbolo} {texto_delta}</span>"
            else:
                ranking_info = "<span style='color:gray;'>sem ranking</span>"

            st.markdown(
                f"<h4 style='margin-bottom:0;'><b>{fundo}</b> {ranking_info}</h4>",
                unsafe_allow_html=True
            )

        with col2:
            score = df_ranking_final[df_ranking_final["Fundo"] == fundo]["Score_Final"].values[0]
            st.markdown(f"### Score Final: **{score:.2f}**")

        import altair as alt

        with st.expander("📉 Ver gráfico DY vs CDI"):
            try:
                if fundo not in df_dy_mensal.columns:
                    st.warning(f"Fundo {fundo} não encontrado em df_dy_mensal.")
                else:
                    janela = 6
                    min_periodos = 3

                    # --- Suavização do DY e CDI ---
                    dy_suavizado = df_dy_mensal[fundo].rolling(window=janela, min_periods=min_periodos).mean()
                    cdi_suavizado = serie_cdi.rolling(window=janela, min_periods=min_periodos).mean()

                    # --- Combinação em único DataFrame ---
                    df_plot = pd.DataFrame({
                        "MesAno": dy_suavizado.index,
                        "DY": dy_suavizado.values,
                        "CDI": cdi_suavizado.reindex(dy_suavizado.index).values
                    }).dropna()

                    if df_plot.empty:
                        st.info("Dados insuficientes para gerar o gráfico.")
                    else:
                        df_long = df_plot.melt(id_vars="MesAno", var_name="Indicador", value_name="Valor")
                        df_long["MesAno"] = pd.to_datetime(df_long["MesAno"], errors="coerce")

                        chart = alt.Chart(df_long).mark_line().encode(
                            x=alt.X("MesAno:T", title="MesAno"),
                            y=alt.Y("Valor:Q", title="Taxa anualizada"),
                            color=alt.Color("Indicador:N", scale=alt.Scale(scheme="category10")),
                            tooltip=["MesAno:T", "Indicador:N", "Valor:Q"]
                        ).properties(
                            title=f"{fundo} – DY vs CDI",
                            width=800,
                            height=350
                        ).interactive()

                        st.altair_chart(chart, use_container_width=True)

            except Exception as e:
                st.warning(f"Erro ao gerar gráfico dinâmico: {e}")

        # Gerar sinais macro
        sinais = gerar_sinais_para_fundo(
            [resultado], df_dy_diario, df_merged, correlacoes_por_variavel, categoria
        )
        sinal_final = sintetizar_sinal_final(sinais)

        st.markdown(f"#### 🧠 Tese Macroeconômica: **{sinal_final}**")

        with st.expander("🔍 Ver detalhes da tese macro"):
            linhas_tabela = ""

            for _, row in df_corr.iterrows():
                variavel = row["Variável"]
                corr = row["Correlação"]
                lag = row["Defasagem"]

                # Detecta categoria do fundo se "Todas" foi selecionado
                if categoria == "Todas":
                    categoria_fundo = next(
                        (cat for cat, lista in estrategias_fiis_reorganizado.items() if fundo in lista),
                        None
                    )
                else:
                    categoria_fundo = categoria

                # Usa a categoria descoberta para buscar no dicionário
                if categoria_fundo:
                    tipo_corr = correlacoes_por_variavel.get(variavel.strip(), {}).get(categoria_fundo.strip(), "N/A")
                else:
                    tipo_corr = "N/A"

                # Variação Macro
                try:
                    serie_macro = df_merged[["MesAno", variavel]].dropna()
                    serie_macro["MesAno"] = pd.to_datetime(serie_macro["MesAno"], format="%m/%Y", errors="coerce")
                    serie_macro.set_index("MesAno", inplace=True)
                    serie_macro = serie_macro[variavel].sort_index()

                    lag = int(row["Defasagem"])
                    ultima_data = serie_macro.index.max()
                    data_fim = ultima_data - relativedelta(months=lag)
                    data_inicio = data_fim - relativedelta(months=1)

                    limite_macro = (serie_macro - serie_macro.mean()).abs().mean()
                    trecho_macro = serie_macro.loc[data_inicio:data_fim]
                    variacao_macro = trecho_macro.sum()

                    if variacao_macro > limite_macro:
                        simbolo_macro = "▲"
                        cor_macro = "green"
                    elif variacao_macro < -limite_macro:
                        simbolo_macro = "▼"
                        cor_macro = "red"
                    else:
                        simbolo_macro = "→"
                        cor_macro = "gray"

                except:
                    variacao_macro = 0
                    simbolo_macro = "?"
                    cor_macro = "black"

                linhas_tabela += f"""
            <tr>
            <td style="border: 1px solid #ddd; padding: 8px;">{variavel}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">{tipo_corr or "N/A"}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">{corr:.2f}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">{lag}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">
            <span style="color:{cor_macro}; font-weight:500;">{simbolo_macro} {variacao_macro:+.2f}%</span>
            </td>
            </tr>
            """

            # ⬇️ Agora só monta e exibe o HTML se houver dados
            if linhas_tabela:
                cards_html = f"""
                <table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; margin-top: 10px;">
                <thead>
                <tr style="background-color: #f2f2f2;">
                <th style="border: 1px solid #ddd; padding: 8px;">Variável</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Tipo de Correlação</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Correlação</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Lag (meses)</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Variação Macro</th>
                </tr>
                </thead>
                <tbody>
                {linhas_tabela}
                </tbody>
                </table>
                """
                st.markdown(cards_html, unsafe_allow_html=True)
            else:
                st.info("⚠️ Nenhuma correlação disponível para exibir para este fundo.")


        # Tese Quantitativa
        sinal_quant = "NEUTRO"
        for item in resultados_teses_quant:
            if item["Fundo"] == fundo:
                sinal_quant = item["Sinal"]
                break

        st.markdown(f"#### 📊 Tese Quantitativa: **{sinal_quant}**")

        with st.expander("📋 Ver detalhamento do score quantitativo"):

            # Scores individuais
            ultimos_dias = df_score1["Data"].tail(5).tolist()
            s1 = df_score1[df_score1["Data"].isin(ultimos_dias)][fundo].mean()
            s2 = df_score2[df_score2["Data"].isin(ultimos_dias)][fundo].mean()
            s3 = df_score3[df_score3["Data"].isin(ultimos_dias)][fundo].mean()
            s4 = df_score4[df_score4["Data"].isin(ultimos_dias)][fundo].mean()

            # Bloco de notas por métrica em HTML com estilo refinado
            tabela_metricas = f"""
<table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; margin-top: 8px;">
<thead>
<tr style="background-color: #f2f2f2;">
<th style="border: 1px solid #ddd; padding: 10px; text-align: left;">Métrica</th>
<th style="border: 1px solid #ddd; padding: 10px; text-align: left;">Nota</th>
<th style="border: 1px solid #ddd; padding: 10px; text-align: left;">Origem</th>
</tr>
</thead>
<tbody>
<tr>
<td style="border: 1px solid #ddd; padding: 10px;">Consistência (21 dias)</td>
<td style="border: 1px solid #ddd; padding: 10px;">{round(s1, 2)}</td>
<td style="border: 1px solid #ddd; padding: 10px;">% dias positivos em janela</td>
</tr>
<tr>
<td style="border: 1px solid #ddd; padding: 10px;">Força (5/21/63)</td>
<td style="border: 1px solid #ddd; padding: 10px;">{round(s2, 2)}</td>
<td style="border: 1px solid #ddd; padding: 10px;">Médias de alfas 5/21/63d</td>
</tr>
<tr>
<td style="border: 1px solid #ddd; padding: 10px;">Acumulado (63d)</td>
<td style="border: 1px solid #ddd; padding: 10px;">{round(s3, 2)}</td>
<td style="border: 1px solid #ddd; padding: 10px;">Soma de alfas em 3 meses</td>
</tr>
<tr>
<td style="border: 1px solid #ddd; padding: 10px;">Volatilidade (126d)</td>
<td style="border: 1px solid #ddd; padding: 10px;">{round(s4, 2)}</td>
<td style="border: 1px solid #ddd; padding: 10px;">Desvio padrão dos alfas</td>
</tr>
</tbody>
</table>
"""

            st.markdown("**Notas por métrica:**", unsafe_allow_html=True)
            st.markdown(tabela_metricas, unsafe_allow_html=True)


            # Sinal detalhado
            linha = df_resultado[df_resultado["Fundo"] == fundo]
            if not linha.empty:
                score_final = linha["Score_Final"].values[0]
                media_5d = linha["Media_5d"].values[0]
                media_21d = linha["Media_21d"].values[0]
                pvp = linha["P/VP"].values[0]
                dy = linha["Dividend_Yield"].values[0]
                sinal = linha["Sinal"].values[0]

                cor = {
                    "Comprar": "#2E7D32",
                    "Vender": "#C62828",
                    "Neutro": "#555"
                }.get(sinal, "#555")

                # HTML visual
                html = f"""
<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; font-family: Arial, sans-serif; margin-top: 10px;">

<div style="border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; background-color: #fafafa; text-align: center;">
<div style="font-size: 14px; color: #666;">Score Final</div>
<div style="font-size: 22px; font-weight: bold;">{score_final}</div>
</div>

<div style="border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; background-color: #fafafa; text-align: center;">
<div style="font-size: 14px; color: #666;">Média 5 dias</div>
<div style="font-size: 22px; font-weight: bold;">{media_5d}</div>
</div>

<div style="border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; background-color: #fafafa; text-align: center;">
<div style="font-size: 14px; color: #666;">Média 21 dias</div>
<div style="font-size: 22px; font-weight: bold;">{media_21d}</div>
</div>

<div style="border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; background-color: #fafafa; text-align: center;">
<div style="font-size: 14px; color: #666;">P/VP</div>
<div style="font-size: 22px; font-weight: bold;">{round(pvp,2)}</div>
</div>

<div style="border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; background-color: #fafafa; text-align: center;">
<div style="font-size: 14px; color: #666;">Dividend Yield</div>
<div style="font-size: 22px; font-weight: bold;">{dy}</div>
</div>

<div style="border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; background-color: #fafafa; text-align: center;">
<div style="font-size: 14px; color: #666;">Sinal Quantitativo</div>
<div style="font-size: 22px; font-weight: bold; color:{cor};">{sinal.upper()}</div>
</div>

</div>
"""


                st.markdown(html, unsafe_allow_html=True)


        st.markdown("---")

