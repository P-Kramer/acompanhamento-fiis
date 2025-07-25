
def pagina_FIIs ():
    from main import menu_principal
    import streamlit as st
    import pandas as pd
    import requests
    from datetime import date, timedelta
    from bs4 import BeautifulSoup
    import os
    import re
    from io import BytesIO
    import json


    if st.button("⬅️ Voltar ao menu"):
        st.session_state.pagina = "menu"
        
    if st.session_state.pagina == "menu":
        menu_principal()
        st.rerun()
    # --- Persistência de Favoritos ---
    CAMINHO_FAVORITOS = "favoritos.json"

    def carregar_favoritos():
        if os.path.exists(CAMINHO_FAVORITOS):
            with open(CAMINHO_FAVORITOS, "r") as f:
                return json.load(f)
        return []

    def salvar_favoritos(lista):
        with open(CAMINHO_FAVORITOS, "w") as f:
            json.dump(lista, f)



    # --- Funções ---
    def buscar_noticias(fii, data_inicial_str, data_final_str):
        palavra_chave = re.sub(r'\d+', '', fii)
        url = "https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/ListarTitulosNoticias"
        params = {
            "agencia": 18,
            "palavra": palavra_chave,
            "dataInicial": data_inicial_str,
            "dataFinal": data_final_str
        }
        res = requests.get(url, params=params)
        if res.status_code == 200:
            noticias = res.json()
            return [
                {
                    "Fundo": fii,
                    "Data": n.get("NwsMsg", {}).get("dateTime", "sem data"),
                    "Título": n.get("NwsMsg", {}).get("headline", "sem título")
                }
                for n in noticias if n.get("NwsMsg")
            ]
        return []

    def get_ultimo_dividendo(ticker):
        url = f"https://statusinvest.com.br/fundos-imobiliarios/{ticker.lower()}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        linha = soup.select_one("table tbody tr")
        if linha:
            colunas = linha.find_all("td")
            if len(colunas) >= 4:
                try:
                    valor = float(colunas[3].text.strip().replace("R$", "").replace(",", "."))
                    return {
                        "Fundo": ticker.upper(),
                        "Data-Base": colunas[1].text.strip(),
                        "Pagamento": colunas[2].text.strip(),
                        "Último Dividendo (R$)": valor
                    }
                except:
                    pass
        return {
            "Fundo": ticker.upper(),
            "Data-Base": None,
            "Pagamento": None,
            "Último Dividendo (R$)": None
        }

    # --- Layout ---
    st.set_page_config("Analisador FIIs", layout="wide")
    st.title("🔍 Analisador de FIIs - Notícias e Dividendos")

    # --- Lista FIIs ---
    todos_fiis =  [
        'HGRU11', 'KEVE11', 'BTAL11', 'XPML11', 'JSRE11', 'TVRI11',
        'RECR11', 'KNRI11', 'RBRF11', 'MXRF11', 'RZTR11', 'XPCI11', 'BRCO11', 'HGRE11', 'VGIR11',
        'XPLG11', 'CPTS11', 'ALZR11', 'KFOF11', 'IRDM11', 'RBRR11', 'KNHF11', 'VISC11', 'HGLG11', 'VIUR11',
        'BTLG11',  'KNHY11', 'MCCI11', 'RBRY11', 'KNSC11', 'PVBI11', 'HSML11', 'KNUQ11', 'KNCR11',
        'LVBI11', 'FATN11', 'GGRC11', 'KORE11', 'TRXF11', 'HGCR11', 'HGFF11', 'VINO11', 'TGAR11', 'KNIP11',
        'RBVA11', 'VILG11', 'VCJR11'
    ]

    # --- Estado global ---
    def init_session():
        if "favoritos" not in st.session_state:
            st.session_state.favoritos = carregar_favoritos()
        if "filtro" not in st.session_state:
            st.session_state.filtro = ""
        for fii in todos_fiis:
            if f"chk_{fii}" not in st.session_state:
                st.session_state[f"chk_{fii}"] = False

    init_session()

    # --- Input de datas com calendário ---
    hoje = date.today()
    min_date = hoje - timedelta(days=30)
    data_inicial = st.date_input(
        "Selecione a data inicial para as notícias",
        min_value=min_date,
        max_value=hoje,
        value=hoje - timedelta(days=3),
        format="DD/MM/YYYY"
    )
    data_final = hoje  # Sempre hoje
    data_inicial_str = data_inicial.strftime("%Y-%m-%d")
    data_final_str = data_final.strftime("%Y-%m-%d")


    # --- Filtro ---
    filtro = st.text_input("🔎 Filtrar FIIs por nome ou ticker:", value=st.session_state.get("filtro", ""), key="filtro_input")
    fiis_filtrados = [f for f in todos_fiis if st.session_state["filtro_input"].upper() in f.upper()]
    fiis_filtrados.sort()


    # --- Ações ---
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Selecionar Todos"):
            for fii in fiis_filtrados:
                st.session_state[f"chk_{fii}"] = True
    with col2:
        if st.button("Limpar Seleção"):
            for fii in fiis_filtrados:
                st.session_state[f"chk_{fii}"] = False
    with col3:
        if st.button("Selecionar Favoritos"):
            for fii in fiis_filtrados:
                st.session_state[f"chk_{fii}"] = fii in st.session_state.favoritos

    # --- Título seção seleção ---
    st.markdown("### 🎯 Selecione os FIIs a analisar:")

    # --- Lista com checkboxes e estrelas em 3 colunas ---
    cols = st.columns(3)
    for i, fii in enumerate(fiis_filtrados):
        with cols[i % 3]:
            col_star, col_chk = st.columns([0.15, 0.85])
            with col_star:
                icone = "⭐" if fii in st.session_state.favoritos else "☆"
                if st.button(icone, key=f"fav_{fii}"):
                    if fii in st.session_state.favoritos:
                        st.session_state.favoritos.remove(fii)
                    else:
                        st.session_state.favoritos.append(fii)
                    salvar_favoritos(st.session_state.favoritos)
                    st.rerun()
            with col_chk:
                st.checkbox(
                    fii,
                    value=st.session_state[f"chk_{fii}"],
                    key=f"chk_{fii}"
                )

    # --- Botão Analisar ---
    selecionados = [fii for fii in todos_fiis if st.session_state.get(f"chk_{fii}", False)]

    if st.button("🚀 Analisar Selecionados") and selecionados:
        with st.spinner("🔄 Coletando dados..."):
            todas_noticias = sum(
                [buscar_noticias(fii, data_inicial_str, data_final_str) for fii in selecionados], []
            )
            df_noticias = pd.DataFrame(todas_noticias)
            dividendos_atuais = [get_ultimo_dividendo(fii) for fii in selecionados]
            df_atuais = pd.DataFrame(dividendos_atuais)

            historico_path = "historico_dividendos.csv"
            if os.path.exists(historico_path):
                df_anterior = pd.read_csv(historico_path)
            else:
                df_anterior = pd.DataFrame(columns=["Fundo", "Data-Base", "Pagamento", "Último Dividendo (R$)"])

            def comparar(row):
                anterior = df_anterior[df_anterior["Fundo"] == row["Fundo"]]
                if anterior.empty:
                    return "NOVO"
                elif row["Data-Base"] != anterior["Data-Base"].values[0]:
                    return "NOVA DATA-BASE"
                elif row["Último Dividendo (R$)"] != anterior["Último Dividendo (R$)"].values[0]:
                    return "VALOR ALTERADO"
                return "IGUAL"

            df_atuais["Status"] = df_atuais.apply(comparar, axis=1)
            df_atuais.to_csv(historico_path, index=False)

            # --- Excel com formatação ---

            from openpyxl import load_workbook
            from openpyxl.styles import Font, Alignment, PatternFill, Border
            from openpyxl.utils import get_column_letter

            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_noticias.to_excel(writer, sheet_name="Notícias", index=False)
                df_atuais.to_excel(writer, sheet_name="Dividendos", index=False)
            buffer.seek(0)

            wb = load_workbook(buffer)

            for ws in wb.worksheets:
                # Cabeçalho
                header_font = Font(bold=True, color="FFFFFF", size=12)
                header_fill = PatternFill("solid", fgColor="4472C4")
                for cell in ws[1]:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = Border()

                # Dados
                for row in ws.iter_rows(min_row=2):
                    for cell in row:
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                        cell.border = Border()

                # Largura automática das colunas
                for col in ws.columns:
                    max_length = 0
                    col_letter = get_column_letter(col[0].column)
                    for cell in col:
                        if cell.value is not None:
                            value_length = len(str(cell.value))
                            if value_length > max_length:
                                max_length = value_length
                    ws.column_dimensions[col_letter].width = max(15, min(max_length + 2, 80))

                # Esconde gridlines no Excel
                ws.sheet_view.showGridLines = False

            output = BytesIO()
            wb.save(output)
            output.seek(0)

            
        st.markdown ("📰 Notícias Recentes")
        with st.expander("Mostrar/Ocultar", expanded=True):
            if df_noticias.empty:
                st.info("Nenhuma notícia encontrada.")
            else:
                st.dataframe(df_noticias)

        st.markdown ("💰 Comparativo de Dividendos")
        with st.expander("Mostrar/Ocultar", expanded=True):
            st.dataframe(df_atuais)
            alterados = df_atuais[df_atuais["Status"] == "VALOR ALTERADO"]
            if not alterados.empty:
                st.warning("⚠️ Fundos com alteração no dividendo:")
                for _, row in alterados.iterrows():
                    fundo = row["Fundo"]
                    atual = row["Último Dividendo (R$)"]
                    anterior = df_anterior[df_anterior["Fundo"] == fundo]["Último Dividendo (R$)"].values[0]
                    st.markdown(f"🔺 **{fundo}**: R$ {anterior:.2f} ➜ R$ {atual:.2f}")

        st.download_button(
        "⬇️ Baixar Excel com Dados",
        data=output,
        file_name="FIIs_noticias_dividendos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"




    )
