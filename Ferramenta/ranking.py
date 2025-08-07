import streamlit as st
import pandas as pd

# Importa os dataframes que já devem estar prontos em outro módulo
from top_fundos import df_ranking_final, df_score1, df_score2, df_score3, df_score4

def pagina_ranking():
    st.set_page_config("Ranking FIIs", layout="wide")
    st.title("📊 Ranking Final de FIIs")

    # Verifica se o DataFrame existe e tem dados
    if df_ranking_final.empty:
        st.warning("⚠️ Nenhum dado disponível para exibir o ranking.")
        return

    # Exibe o ranking final ordenado por score final
    df_ordenado = df_ranking_final.sort_values(by="Score Final", ascending=False).reset_index(drop=True)

    # Renomeia as colunas (se necessário) e reorganiza
    colunas_desejadas = ["Fundo", "Score 1", "Score 2", "Score 3", "Score 4", "Score Final"]
    df_exibicao = df_ordenado[colunas_desejadas]

    # Adiciona coluna de posição no ranking
    df_exibicao.index += 1
    df_exibicao.reset_index(inplace=True)
    df_exibicao.rename(columns={"index": "🏅 Posição"}, inplace=True)

    st.dataframe(df_exibicao.style.set_properties(**{"text-align": "center"}))
