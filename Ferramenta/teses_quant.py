import pandas as pd
from PVPs_DY import dados_fiis
import streamlit as st

alfas = st.session_state.get("alfas")
df_ranking_final = st.session_state.get("df_ranking_final")

# ✅ Agora fora de qualquer loop
resultados_teses_quant = []

# ✅ Único for necessário
for _, row in df_ranking_final.iterrows():
    fundo = row["Fundo"]
    score_final = float(row["Score_Final"])

    def gerar_sinal(score_final, media_5d, media_21d, pvp):
        if score_final is None or media_5d is None or media_21d is None or pvp is None:
            return "Neutro"

        tendencia = "alta" if media_5d > media_21d else "queda"

        if score_final > 6 and tendencia == "queda" and pvp > 0.9 and media_5d < 0:
            return "Vender"
        elif score_final >= 5.5 and tendencia == "alta" and pvp < 0.95:
            return "Comprar"
        else:
            return "Neutro"

    if fundo in alfas.columns and fundo in dados_fiis:
        media_5d = alfas[fundo].tail(5).mean()
        media_21d = alfas[fundo].tail(21).mean()
        pvp = float(dados_fiis[fundo]["PVP"])
        dy = float(dados_fiis[fundo]["Dividend_Yield"][:-1])
        sinal = gerar_sinal(score_final, media_5d, media_21d, pvp)

        resultados_teses_quant.append({
            "Fundo": fundo,
            "Score_Final": round(score_final, 2),
            "Media_5d": round(media_5d * 100, 3),
            "Media_21d": round(media_21d * 100, 2),
            "P/VP": pvp,
            "Dividend_Yield": round(dy, 2),
            "Sinal": sinal
        })

df_resultado = pd.DataFrame(resultados_teses_quant)

st.session_state["resultados_teses_quant"] = resultados_teses_quant
st.session_state["df_resultado"] = df_resultado
