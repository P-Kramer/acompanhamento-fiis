import pandas as pd
from PVPs_DY import dados_fiis
from top_fundos import df_ranking_final
from alfas import alfas


# Função para gerar o sinal
def gerar_sinal(score_final, media_5d, media_21d, pvp):
    if score_final is None or media_5d is None or media_21d is None or pvp is None:
        return "NEUTRO"

    tendencia = "alta" if media_5d > media_21d else "queda"

    if score_final > 6 and tendencia == "queda" and pvp > 0.9 and media_5d < 0:
        return "VENDER"
    elif score_final >= 5.5 and tendencia == "alta" and pvp < 0.95:
        return "COMPRAR"
    else:
        return "NEUTRO"

# Construir a tabela final com DY incluso
resultados = []

for _, row in df_ranking_final.iterrows():
    fundo = row["Fundo"]
    score_final = float(row["Score_Final"])

    if fundo in alfas.columns and fundo in dados_fiis:
        media_5d = alfas[fundo].tail(5).mean()
        media_21d = alfas[fundo].tail(21).mean()
        pvp = float(dados_fiis[fundo]["PVP"])
        dy = float(dados_fiis[fundo]["Dividend_Yield"][:-1])
        sinal = gerar_sinal(score_final, media_5d, media_21d, pvp)

        resultados.append({
            "Fundo": fundo,
            "Score_Final": round(score_final,2),
            "Media_5d": f'{round(media_5d*100,3)}%',
            "Media_21d": f'{round(media_21d*100,2)}%',
            "P/VP": pvp,
            "Dividend_Yield": f'{round(dy, 2)}%',
            "Sinal": sinal
        })

df_resultado = pd.DataFrame(resultados)
print(df_resultado)
