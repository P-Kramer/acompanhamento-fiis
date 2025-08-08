import streamlit as st
from pathlib import Path
from PIL import Image

st.set_page_config("Ferramenta de Análise de FIIs", layout="wide")

# Logo da sidebar
logo_path = Path(__file__).parent / "logo_sidebar.png"
logo_img = Image.open(logo_path) if logo_path.exists() else None

# === Sidebar ===
with st.sidebar:
    st.markdown("""<style> ... </style>""", unsafe_allow_html=True)

    if logo_img:
        st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
        st.image(logo_img, width=140)
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
    st.markdown("<div style='font-size: 0.85rem; color: #ccc;'>© 2025 - Longview Analytics</div>", unsafe_allow_html=True)

# === PÁGINA INICIAL ===
from pagina_inicial import pagina_inicial

if selecao == "Página inicial":
    pagina_inicial()

# === BLOQUEIO GLOBAL ===
if "arquivo" not in st.session_state:
    st.warning("⚠️ Nenhum arquivo carregado ainda. Para acessar as demais páginas, envie o arquivo Precos_Reuters.xlsm na Página Inicial.")
    st.stop()

# Garante que as variáveis macro estejam carregadas
from dados import carregar_variaveis_macro

if "df_merged" not in st.session_state or "correlacoes_por_variavel" not in st.session_state:
    carregar_variaveis_macro(st.session_state["arquivo"])


# === IMPORTS POSTERIORES APENAS COM ARQUIVO DISPONÍVEL ===
from Noticias import pagina_FIIs
from analises import pagina_resultados
from ranking import pagina_ranking

# === OUTRAS PÁGINAS ===
def pagina_premissas():
    st.markdown("<h2>⚙️ Ranking</h2>", unsafe_allow_html=True)
    st.info("Esta seção está em desenvolvimento.")

if selecao == "Divulgações":
    pagina_FIIs()
elif selecao == "Análises":
    pagina_resultados()
elif selecao == "Ranking":
    pagina_ranking()
elif selecao == "Premissas":
    pagina_premissas()
