import streamlit as st
from top_fundos import (
    df_ranking_final,
    df_score1,
    df_score2,
    df_score3,
    df_score4,
    df_ranking_retroativo,
)
import pandas as pd

def render_tabela_html(df, titulo, cor_header="#f2f2f2"):
    linhas_tabela = ""
    for _, row in df.iterrows():
        linhas_tabela += "<tr>"
        for valor in row:
            linhas_tabela += f"""
<td style="border: 1px solid #ddd; padding: 8px; text-align:center;">{valor}</td>
"""
        linhas_tabela += "</tr>"

    html = f"""
<table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; margin-top: 10px;">
<thead>
    <tr style="background-color: {cor_header}; text-align:center;">
        {''.join([f'<th style="border: 1px solid #ddd; padding: 8px;">{col}</th>' for col in df.columns])}
    </tr>
</thead>
<tbody>
    {linhas_tabela}
</tbody>
</table>
"""
    with st.expander(titulo, expanded=False):
        st.markdown(html, unsafe_allow_html=True)

def pagina_ranking():
    if not st.session_state.get("arquivo", False):
        st.warning("⚠ Por favor, carregue o arquivo na Página Inicial antes de continuar.")
        st.stop()
    st.set_page_config("Ranking FIIs", layout="wide")
    st.title("📊 Ranking dos FIIs")
    # Explicação do Score Final
    st.markdown("""
    *📌 Como é calculado o Ranking Final?*

    O ranking final combina os quatro scores individuais com os seguintes pesos:
    - *Consistência* (frequência de alfa positivo): *30%*
    - *Força* (intensidade do alfa): *25%*
    - *Acumulado* (alfa somado nos últimos 63 dias): *25%*
    - *Volatilidade* (quanto menos oscilação, melhor): *20%*

    A nota final de cada fundo é ponderada por esses critérios nos últimos 5 dias úteis.
    """)


    ultimos_scores = []
    scores = [df_score1, df_score2, df_score3, df_score4]
    nomes_colunas = ["Score 1", "Score 2", "Score 3", "Score 4"]

    for i, df_score in enumerate(scores):
        ultima_data = df_score["Data"].max()
        df_tmp = df_score[df_score["Data"] == ultima_data].copy()
        df_tmp.set_index("Data", inplace=True)
        df_tmp = df_tmp.T.reset_index().rename(columns={"index": "Fundo", ultima_data: nomes_colunas[i]})
        ultimos_scores.append(df_tmp)

    df_all_scores = ultimos_scores[0]
    for i in range(1, 4):
        df_all_scores = df_all_scores.merge(ultimos_scores[i], on="Fundo", how="outer")

    df = df_ranking_final.copy()
    df.columns = ["Fundo", "Score Final"]
    df = df.merge(df_all_scores, on="Fundo", how="left")

    df = df.sort_values("Score Final", ascending=False).reset_index(drop=True)
    df["Ranking Anterior"] = df["Fundo"].map({f: i + 1 for i, f in enumerate(df_ranking_retroativo["Fundo"])}).fillna(len(df) + 1).astype(int)
    df.insert(0, "Posição", df.index + 1)
    df["Variação"] = df["Ranking Anterior"] - df["Posição"]

    def format_variacao(v):
        if v > 0:
            return f'<span style="color:green; font-weight:500;">▲ {v}</span>'
        elif v < 0:
            return f'<span style="color:red; font-weight:500;">▼ {abs(v)}</span>'
        else:
            return f'<span style="color:black; font-weight:500;">→ 0</span>'
    
    df["Score Final"] = df["Score Final"].round(2)
    df["Variação"] = df["Variação"].apply(format_variacao)


    render_tabela_html(df[["Posição", "Fundo", "Score 1", "Score 2", "Score 3", "Score 4", "Score Final", "Variação"]],
                       titulo="🏆 Ranking Final dos FIIs")

    score_labels = ["Consistência", "Força", "Acumulado", "Volatilidade"]
    score_dfs = [df_score1, df_score2, df_score3, df_score4]

    for i, (nome, df_score) in enumerate(zip(score_labels, score_dfs), start=1):
        ultima_data = df_score["Data"].max()
        df_atual = df_score[df_score["Data"] == ultima_data].copy()
        df_atual.set_index("Data", inplace=True)
        df_atual = df_atual.T.reset_index().rename(columns={"index": "Fundo", ultima_data: "Nota Atual"})
        df_atual["Nota Atual"] = pd.to_numeric(df_atual["Nota Atual"], errors="coerce")
        df_atual = df_atual.sort_values("Nota Atual", ascending=False).reset_index(drop=True)
        df_atual.insert(0, "Ranking Atual", df_atual.index + 1)

        data_retroativa = df_score["Data"].iloc[-21] if len(df_score) > 21 else None
        if data_retroativa:
            df_antigo = df_score[df_score["Data"] == data_retroativa].copy()
            df_antigo.set_index("Data", inplace=True)
            df_antigo = df_antigo.T.reset_index().rename(columns={"index": "Fundo", data_retroativa: "Nota Antiga"})
            df_antigo["Nota Antiga"] = pd.to_numeric(df_antigo["Nota Antiga"], errors="coerce")
            df_antigo = df_antigo.sort_values("Nota Antiga", ascending=False).reset_index(drop=True)
            df_antigo.insert(0, "Ranking Antigo", df_antigo.index + 1)
        else:
            df_antigo = pd.DataFrame(columns=["Fundo", "Nota Antiga", "Ranking Antigo"])

        df_comparativo = df_atual.merge(df_antigo[["Fundo", "Nota Antiga", "Ranking Antigo"]], on="Fundo", how="left")

        def format_rank_var(row):
            try:
                atual = row["Ranking Atual"]
                antigo = row["Ranking Antigo"]
                if pd.isna(antigo):
                    return "-"
                delta = antigo - atual
                if delta > 0:
                    return f'<span style="color:green; font-weight:500;">▲ {delta}</span>'
                elif delta < 0:
                    return f'<span style="color:red; font-weight:500;">▼ {abs(delta)}</span>'
                else:
                    return f'<span style="color:black; font-weight:500;">→ 0</span>'
            except:
                return "-"

        df_comparativo["Variação de Posição"] = df_comparativo.apply(format_rank_var, axis=1)
        df_comparativo = df_comparativo[["Ranking Atual", "Fundo", "Nota Atual", "Variação de Posição"]]
        df_comparativo = df_comparativo.rename(columns={"Ranking Atual": "Posição"})

                # Explicações para cada score
        explicacoes = {
            "Consistência": """
*🔍 O que é Consistência?*  
Este score mede a *frequência com que o fundo superou o CDI* nos últimos 21 dias úteis.  
- Se o fundo teve alfa positivo em todos os dias → nota 10  
- Se nunca teve alfa positivo → nota 0  
""",
            "Força": """
*💪 O que é Força?*  
A força representa a *intensidade média dos retornos acima do CDI* em 3 janelas (5, 21 e 63 dias úteis), com mais peso nos dias mais recentes.  
Quanto maior o retorno médio ajustado, maior a nota.  
""",
            "Acumulado": """
*📈 O que é Acumulado?*  
Soma dos alfas (retornos sobre o CDI) nos últimos 63 dias úteis.  
- Alfa acumulado ≥ +10% → nota 10  
- Alfa acumulado ≤ -10% → nota 0  
""",
            "Volatilidade": """
*🎯 O que é Volatilidade?*  
Avalia *o quanto os retornos do fundo oscilam*.  
- Quanto *menor o desvio padrão dos alfas*, maior a nota.  
- Se o fundo tem retornos estáveis → nota próxima de 10  
- Se é muito volátil → nota próxima de 0  
"""
        }

        st.markdown(explicacoes.get(nome, ""), unsafe_allow_html=True)


        render_tabela_html(df_comparativo, titulo=f"📊 Ranking: {nome}")