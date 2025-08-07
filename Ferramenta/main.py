import streamlit as st
from pathlib import Path
from PIL import Image
import os

from Noticias import pagina_FIIs
from analises import pagina_resultados
from ranking import pagina_ranking
from pagina_inicial import pagina_inicial

# Configuração geral da página
st.set_page_config("Ferramenta de Análise de FIIs", layout="wide")

logo_path = Path(__file__).parent / "logo_sidebar.png"
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

def pagina_premissas():
    if not st.session_state.get("arquivo", False):
        st.warning("⚠ Por favor, carregue o arquivo na Página Inicial antes de continuar.")
        st.stop()

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
    pagina_ranking()
elif selecao == "Premissas":
    pagina_premissas()
