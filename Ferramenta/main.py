import streamlit as st
from pathlib import Path
from PIL import Image
import os

from Noticias import pagina_FIIs
from analises import pagina_resultados

# Configuração geral da página
st.set_page_config("Ferramenta de Análise de FIIs", layout="wide")

# Caminho da logo
logo_path = os.path.abspath("logo_sidebar.png")
logo_img = Image.open(logo_path) if logo_path.exists() else None

with st.sidebar:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #3a3a3a;
        border-right: 1px solid #ddd;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    div[data-testid="stSidebar"] label:hover {
        background-color: #4a4a4a;
        color: #ffffff !important;
    }

    div[data-testid="stSidebar"] input:checked + div > label {
        background-color: #444;
        font-weight: 600;
        border-left: 4px solid #5e9bff;
        color: #ffffff !important;
    }

    .logo-container {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # ✅ Exibir logo centralizada e maior
    if logo_img:
        st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
        st.image(logo_img, width=140)  # Aumente o width aqui conforme desejar
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Logo não encontrada.")

    selecao = st.radio(
        label="",
        options=["Página inicial", "Divulgações", "Análises", "Ranking", "Premissas"],
        index=0,
        key="menu_sidebar"
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size: 0.85rem; color: #ccc;'>© 2025 - Longview Analytics</div>",
        unsafe_allow_html=True
    )


# PÁGINAS
def pagina_inicial():
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

def pagina_premissas():
    st.markdown("<h2>⚙️ Ranking</h2>", unsafe_allow_html=True)
    st.info("Esta seção está em desenvolvimento.")

# NAVEGAÇÃO PRINCIPAL
if selecao == "Página inicial":
    pagina_inicial()
elif selecao == "Divulgações":
    pagina_FIIs()
elif selecao == "Análises":
    pagina_resultados()
elif selecao == "Ranking":
    pagina_premissas()
elif selecao == "Premissas":
    pagina_premissas()
