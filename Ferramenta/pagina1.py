import streamlit as st
import pandas as pd
import os
from PIL import Image
from glob import glob

from top_fundos import df_ranking_final, df_score1, df_score2, df_score3, df_score4
from lista_fundos_analisados import estrategias_fiis_reorganizado
from pontos_macro import gerar_sinais_para_fundo, sintetizar_sinal_final
from alfas import df_dy_diario
from dados import df_merged, correlacoes_por_variavel
from corr import resultados
from teses_quant import resultados as resultados_teses_quant


def pagina_resultados():
    st.set_page_config("📊 Sinais e Análises", layout="wide")
    st.title("📊 Sinais e Análises por Fundo")

    # Botão para voltar ao menu
    if st.button("⬅️ Voltar ao menu principal"):
        st.session_state.pagina = "menu"
        st.rerun()

    # Filtro por categoria
    categorias = list(estrategias_fiis_reorganizado.keys())
    categoria = st.selectbox("Selecione a categoria", categorias)

    fundos = estrategias_fiis_reorganizado.get(categoria, [])

    for resultado in resultados.get(categoria, []):
        for fundo, df_corr in resultado.items():
            if fundo not in fundos:
                continue

            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(f"{fundo}")
            with col2:
                score = df_ranking_final[df_ranking_final["Fundo"] == fundo]["Score_Final"].values[0]
                cor = "🟢" if score >= 6.5 else "🟡" if score >= 5 else "🔴"
                st.markdown(f"### Score Final: **{score:.2f}** {cor}")

            # Caminho do gráfico (busca flexível)
            arquivos = glob(f"Gráficos/{categoria}/*{fundo}*.png")

            with st.expander("📉 Ver gráfico DY vs CDI"):
                if arquivos:
                    st.image(arquivos[0], caption="DY vs CDI", use_column_width=True)
                else:
                    st.info("Gráfico não encontrado.")

            # Gerar sinais macro
            sinais = gerar_sinais_para_fundo(
                [resultado], df_dy_diario, df_merged, correlacoes_por_variavel, categoria
            )
            sinal_final = sintetizar_sinal_final(sinais)

            st.markdown(f"#### 🧠 Tese Macroeconômica: **{sinal_final}**")

            with st.expander("🔍 Ver detalhes da tese macro"):
                st.markdown("**Variáveis utilizadas e decisões parciais:**")
                for _, row in df_corr.iterrows():
                    variavel = row["Variável"]
                    corr = row["Correlação"]
                    lag = row["Defasagem"]
                    tipo_corr = correlacoes_por_variavel.get(variavel, {}).get(categoria)

                    # Inflexões
                    inflexao_macro = "N/A"
                    inflexao_dy = "N/A"
                    try:
                        serie_macro = df_merged.set_index("MesAno")[variavel].dropna()
                        inflexao_macro = "⬆️" if serie_macro.diff().iloc[-1] > 0 else "⬇️"
                    except:
                        pass
                    try:
                        serie_dy = df_dy_diario.set_index("Data")[fundo].dropna()
                        inflexao_dy = "⬆️" if serie_dy.diff().iloc[-1] > 0 else "⬇️"
                    except:
                        pass

                    st.markdown(f"- **{variavel}** ({tipo_corr}) → Corr: `{corr:.2f}` | Lag: `{lag}` | Macro: {inflexao_macro} | DY: {inflexao_dy}")

            # Tese Quantitativa
            sinal_quant = "NEUTRO"
            for item in resultados_teses_quant:
                if item["Fundo"] == fundo:
                    sinal_quant = item["Sinal"]
                    break

            st.markdown(f"#### 📊 Tese Quantitativa: **{sinal_quant}**")

            with st.expander("📋 Ver detalhamento do score quantitativo"):
                ultimos_dias = df_score1["Data"].tail(5).tolist()

                s1 = df_score1[df_score1["Data"].isin(ultimos_dias)][fundo].mean()
                s2 = df_score2[df_score2["Data"].isin(ultimos_dias)][fundo].mean()
                s3 = df_score3[df_score3["Data"].isin(ultimos_dias)][fundo].mean()
                s4 = df_score4[df_score4["Data"].isin(ultimos_dias)][fundo].mean()

                df_expl = pd.DataFrame({
                    "Métrica": ["Consistência (21 dias)", "Força (5/21/63)", "Acumulado (63d)", "Volatilidade (126d)"],
                    "Nota": [round(s1, 2), round(s2, 2), round(s3, 2), round(s4, 2)],
                    "Origem": [
                        "% dias positivos em janela",
                        "Médias de alfas 5/21/63d",
                        "Soma de alfas em 3 meses",
                        "Desvio padrão dos alfas"
                    ]
                })
                st.dataframe(df_expl, use_container_width=True)

            st.markdown("---")
