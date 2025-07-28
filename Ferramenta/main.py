import streamlit as st
from FIIs.Noticias import pagina_FIIs
from pagina1 import pagina_resultados





st.set_page_config("Ferramenta - Menu Principal", layout="centered")

def menu_principal():
    st.markdown("""
    <style>
    /* Centraliza toda a área do menu */
    .menu-flex {
        display: flex;
        justify-content: center;
        gap: 2.5rem;
        margin-top: 2.3rem;
        margin-bottom: 2.3rem;
        flex-wrap: wrap;
    }
    /* Estilo dos botões grandes */
    .stButton > button, .big-btn {
        background: linear-gradient(135deg, #22253b 60%, #393b5b 100%);
        color: #fff;
        font-size: 1.45em !important;
        font-weight: 700 !important;
        border: none;
        border-radius: 2.2em !important;
        padding: 1.5em 2.7em !important;
        box-shadow: 0 6px 26px #0003;
        transition: transform 0.13s, box-shadow 0.21s, background 0.27s;
        cursor: pointer;
        outline: none;
        min-width: 210px;
        min-height: 100px;
        margin-bottom: 0.6em;
        margin-top: 0.6em;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.7em;
        letter-spacing: 0.01em;
        white-space: nowrap;
    }
    .stButton > button:hover, .big-btn:hover {
        background: linear-gradient(135deg, #393b5b 60%, #22253b 100%);
        transform: scale(1.055);
        box-shadow: 0 8px 30px #0005;
    }
    /* Garante que os ícones fiquem centralizados */
    .big-btn span.emoji {
        font-size: 1.4em;
        margin-right: 0.5em;
        vertical-align: middle;
        line-height: 1;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='font-size:2.7em; margin-bottom:0.4em;'>🛠️ Ferramenta - Menu Principal</h1>", unsafe_allow_html=True)
    st.write("Escolha um módulo para acessar:")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 FIIs"):
            st.session_state.pagina = "fiis"
            st.rerun()
    with col2:
        if st.button("📈 Gráficos"):
            st.session_state.pagina = "graficos"
    with col3:
        if st.button("🧮 Modelagem"):
            st.session_state.pagina = "modelagem"

    st.markdown("---")


# --- Controle de navegação ---
if "pagina" not in st.session_state:
    st.session_state.pagina = "menu"

if st.session_state.pagina == "menu":
    menu_principal()
elif st.session_state.pagina == "fiis":
    pagina_FIIs()
elif st.session_state.pagina == "graficos":
    pagina_resultados()
