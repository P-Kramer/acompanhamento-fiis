import streamlit as st
import pandas as pd

from top_fundos import (
    df_ranking_final,
    df_score1,
    df_score2,
    df_score3,
    df_score4,
    ranking_atual,
    ranking_antigo
)

def pagina_ranking():
    st.set_page_config("Ranking FIIs", layout="wide")
    st.title("📊 Ranking Final dos FIIs")

    # Calcula médias dos últimos 5 dias para cada score individual
    ultimos_dias = df_score1["Data"].tail(5).tolist()

    def medias_finais(df_score):
        return df_score[df_score["Data"].isin(ultimos_dias)].drop(columns=["Data"]).mean().round(2)

    media_1 = medias_finais(df_score1)
    media_2 = medias_finais(df_score2)
    media_3 = medias_finais(df_score3)
    media_4 = medias_finais(df_score4)

    # Junta todos os dados em um único DataFrame
    df = df_ranking_final.copy()
    df = df.merge(media_1.rename("Score 1"), on="Fundo")
    df = df.merge(media_2.rename("Score 2"), on="Fundo")
    df = df.merge(media_3.rename("Score 3"), on="Fundo")
    df = df.merge(media_4.rename("Score 4"), on="Fundo")

    # Adiciona posição e (opcionalmente) variação
    df["🏅 Posição"] = df["Fundo"].map(ranking_atual)
    df["📉 Posição Anterior"] = df["Fundo"].map(ranking_antigo)
    df["🔺 Variação"] = df["📉 Posição Anterior"] - df["🏅 Posição"]

    # Ordena pelo ranking atual
    df = df.sort_values("🏅 Posição").reset_index(drop=True)

    # Organiza colunas
    colunas_exibir = [
        "🏅 Posição", "Fundo", "Score 1", "Score 2", "Score 3", "Score 4", "Score_Final", "🔺 Variação"
    ]
    df.rename(columns={"Score_Final": "Score Final"}, inplace=True)
    df = df[colunas_exibir]

    st.dataframe(df.style.format({
        "Score 1": "{:.2f}",
        "Score 2": "{:.2f}",
        "Score 3": "{:.2f}",
        "Score 4": "{:.2f}",
        "Score Final": "{:.2f}",
        "🔺 Variação": "{:+d}"
    }).set_properties(**{"text-align": "center"}))
