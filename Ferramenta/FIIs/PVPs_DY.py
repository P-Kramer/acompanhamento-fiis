import requests
from bs4 import BeautifulSoup
import pandas as pd

from Ferramenta.lista_fundos_analisados import nomes_fundos_limpos

# Função para puxar P/VP e Dividend Yield do Status Invest
def get_pvp_e_dy(fii_ticker):
    url = f"https://statusinvest.com.br/fundos-imobiliarios/{fii_ticker.lower()}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    pvp = None
    dy = None

    indicadores = soup.select("div.top-info div.info")
    for indicador in indicadores:
        titulo = indicador.select_one("h3")
        valor = indicador.select_one("strong")

        if not titulo or not valor:
            continue

        titulo_text = titulo.text.strip()
        valor_text = valor.text.strip().replace(",", ".").replace("%", "")

        if "P/VP" in titulo_text:
            try:
                pvp = float(valor_text)
            except:
                pass
        elif "Dividend Yield" in titulo_text:
            try:
                dy = float(valor_text) / 100
            except:
                pass

    return pvp, dy

# Criar dicionário com os dados
dados_fiis = {}

for fundo in nomes_fundos_limpos:
    pvp, dy = get_pvp_e_dy(fundo)
    dados_fiis[fundo] = {
        "PVP": pvp,
        "Dividend_Yield": f'{round(dy*100,2)}%'
    }

df_dados_fiis = pd.DataFrame.from_dict(dados_fiis, orient="index").reset_index().rename(columns={"index": "Fundo"})