import streamlit as st
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
    with st.expander(titulo, expanded=True):
        st.markdown(html, unsafe_allow_html=True)

def pagina_inicial():
    st.set_page_config("Página Inicial", layout="wide")

    st.markdown("""
    <style>
    .intro-box {
        background-color: #f9f9f9;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        font-family: 'Segoe UI', sans-serif;
        color: #333;
        line-height: 1.6;
        margin-bottom: 2rem;
    }
    .intro-box h1 {
        font-size: 2.2rem;
        color: #222;
        margin-bottom: 1rem;
    }
    .intro-box p {
        font-size: 1.1rem;
        margin-bottom: 0.8rem;
    }
    </style>
    <div class='intro-box'>
        <h1>📊 Ferramenta de Análise de FIIs</h1>
        <p>Esta plataforma combina inteligência macroeconômica e desempenho quantitativo para gerar insights de investimento em fundos imobiliários.</p>
        <p>Utilize o menu à esquerda para:</p>
        <p>🔍 Acompanhar <strong>divulgações e dividendos</strong> mais recentes dos FIIs.</p>
        <p>📈 Explorar <strong>correlações com variáveis macro</strong> e sinais quantitativos de entrada ou saída.</p>
        <p>⚙️ Ajustar <strong>premissas da análise</strong> (em breve).</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 📂 Upload do Arquivo de Estratégias
    Envie o arquivo **Precos_Reuters.xlsm** com os tickers e suas categorias na aba **Preços** (linha 1: tickers, linha 2: categorias).
    """)

    arquivo = st.file_uploader("Arraste ou selecione o arquivo .xlsm", type="xlsm")

    if arquivo:
        try:
            df_precos = pd.read_excel(arquivo, sheet_name="Preços", header=None)
            fundos_raw = df_precos.iloc[0, 2:].dropna().tolist()
            categorias_raw = df_precos.iloc[1, 2:2+len(fundos_raw)].tolist()
            nomes_fundos_limpos = [nome.replace(".SA", "") for nome in fundos_raw]

            estrategias_fiis = dict(zip(nomes_fundos_limpos, categorias_raw))

            estrategias_fiis_reorganizado = {}
            for fundo, categoria in estrategias_fiis.items():
                if categoria not in estrategias_fiis_reorganizado:
                    estrategias_fiis_reorganizado[categoria] = []
                estrategias_fiis_reorganizado[categoria].append(fundo)
            for fundos in estrategias_fiis_reorganizado.values():
                fundos.sort()

            # Armazena no session_state para uso em outras páginas
            st.session_state.arquivo = arquivo
            st.session_state.df_precos = df_precos
            st.session_state.fundos_raw = fundos_raw
            st.session_state.nomes_fundos_limpos = nomes_fundos_limpos
            st.session_state.estrategias_fiis = estrategias_fiis
            st.session_state.estrategias_fiis_reorganizado = estrategias_fiis_reorganizado

            st.success("Arquivo carregado e estratégias extraídas com sucesso!")

            with st.expander("🔍 Visualizar Estratégias por Categoria"):
                for categoria, fundos in estrategias_fiis_reorganizado.items():
                    st.markdown(f"**{categoria}**: {', '.join(fundos)}")

        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

    elif "estrategias_fiis" not in st.session_state:
        st.warning("⚠️ Nenhum arquivo carregado ainda. Para acessar as demais páginas, envie o arquivo Precos_Reuters.xlsm na Página Inicial.")
