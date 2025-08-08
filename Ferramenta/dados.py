# variaveis_macro.py  (ou dados.py)
import pandas as pd
import json
import urllib.request
from datetime import datetime
from functools import reduce
import io
import streamlit as st

def carregar_variaveis_macro(arquivo=None):
    st.write("🔄 Função `carregar_variaveis_macro` executada")

    if arquivo is None:
        arquivo = st.session_state.get("arquivo")
    if arquivo is None:
        st.error("⚠ Nenhum arquivo carregado.")
        return None, None

    try:
        df_variaveis = pd.read_excel(arquivo, sheet_name="Variaveis")
    except Exception as e:
        st.error(f"❌ Erro ao ler a aba 'Variaveis': {e}")
        return None, None

    hoje = datetime.today()
    data_inicio = '02/01/2016'
    data_fim = hoje.strftime('%d/%m/%Y')

    lista_dfs = []
    correlacoes_por_variavel = {}

    for _, row in df_variaveis.iterrows():
        nome = row['Variável']
        fonte = row['Fonte']
        codigo = int(float(row['Código'])) if pd.notna(row['Código']) else None
        transformacao = row.get('Transformação', None)

        correlacoes_por_variavel[nome] = {
            "Pós-fixado": str(row.get("Pós-fixado", "")).strip().lower(),
            "Inflação": str(row.get("Inflação", "")).strip().lower(),
            "Tijolo": str(row.get("Tijolo", "")).strip().lower(),
            "Carrego": str(row.get("Carrego", "")).strip().lower(),
        }

        if fonte == "Bacen" and codigo is not None:
            url = (
                f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
                f"?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}"
            )
            try:
                with urllib.request.urlopen(url) as response:
                    data_json = json.loads(response.read())

                df_raw = pd.DataFrame(data_json)
                df_raw['Data'] = pd.to_datetime(df_raw['data'], format='%d/%m/%Y')
                df_raw[nome] = pd.to_numeric(df_raw['valor'], errors='coerce')
                df_raw = df_raw[['Data', nome]]

                df_raw = df_raw.set_index('Data')
                df_proc = df_raw.resample('ME').last().reset_index()

                if transformacao == 'Pct':
                    df_proc[nome] = df_proc[nome].pct_change()
                    df_proc = df_proc.dropna(subset=[nome])
                elif transformacao == 'Diff':
                    df_proc[nome] = df_proc[nome].diff()
                    df_proc = df_proc.dropna(subset=[nome])
                elif transformacao == "Outro":
                    df_proc = df_proc.dropna(subset=[nome])

                df_proc["MesAno"] = df_proc["Data"].dt.strftime("%m/%Y")
                df_proc = df_proc[["MesAno", nome]]
                lista_dfs.append(df_proc)

            except Exception as e:
                st.warning(f"⚠️ Erro ao processar {nome} (Código {codigo}): {e}")

    # EPU
    try:
        url_epu = 'https://www.policyuncertainty.com/media/Brazil_Policy_Uncertainty_Data.csv'
        response = urllib.request.urlopen(url_epu)
        csv_data = response.read().decode('utf-8')
        df_epu = pd.read_csv(io.StringIO(csv_data))
        df_epu = df_epu[df_epu['year'] >= 2016]
        df_epu["Data"] = pd.to_datetime(dict(year=df_epu["year"], month=df_epu["month"], day=1))
        df_epu = df_epu.rename(columns={"Brazil_Policy_Index": "EPU"})
        df_epu["EPU"] = pd.to_numeric(df_epu["EPU"], errors="coerce").pct_change()
        df_epu["MesAno"] = df_epu["Data"].dt.strftime("%m/%Y")
        df_epu = df_epu.sort_values("Data")[["MesAno", "EPU"]].dropna().reset_index(drop=True)
        lista_dfs.append(df_epu)
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar EPU: {e}")

    if not lista_dfs:
        st.error("❌ Nenhuma variável macroeconômica foi carregada com sucesso.")
        return None, None

    try:
        df_merged = reduce(lambda l, r: pd.merge(l, r, on="MesAno", how="outer"), lista_dfs)
        df_merged["MesAno"] = pd.to_datetime(df_merged["MesAno"], format="%m/%Y")
        df_merged = df_merged.sort_values("MesAno").reset_index(drop=True)
        df_merged["MesAno"] = df_merged["MesAno"].dt.strftime("%m/%Y")

        st.session_state.df_merged = df_merged
        st.session_state.correlacoes_por_variavel = correlacoes_por_variavel
        return df_merged, correlacoes_por_variavel
    except Exception as e:
        st.error(f"❌ Erro ao consolidar dados macroeconômicos: {e}")
        return None, None
