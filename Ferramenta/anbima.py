import requests
import base64
import pandas as pd
import numpy as np


'''
# 1. Função para obter token
def obter_access_token(client_id, client_secret):
    url = "https://api.anbima.com.br/oauth/access-token"
    credenciais = f"{client_id}:{client_secret}"
    credenciais_base64 = base64.b64encode(credenciais.encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {credenciais_base64}"
    }
    payload = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["access_token"]

# 2. Função para consultar o resultado diário do IMA-B
def consultar_resultado_diario_ima_b(token, data):
    base_url = "https://api.anbima.com.br/feed/precos-indices/v2/ima-etf/resultado-diario"
    params = {"etf": "IMA_B"}
    if data:
        params["data"] = data  # Ex: "2024-08-01"

    headers = {
        "Content-Type": "application/json",
        "access_token": token,
        "client_id": client_id
    }

    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# 3. Rodando tudo
client_id = "AKWA9yMGtwpH"
client_secret = "KVsgBiPNiUCZ"
token = obter_access_token(client_id, client_secret)

# Consulta sem data (pega último resultado disponível)
dados = consultar_resultado_diario_ima_b(token,"2017-02-01")

# Exibir como DataFrame
df = pd.DataFrame(dados)
print(df)'''

import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# 1. Gerar dados simulados de IMA-B diário (mock)
def gerar_dados_mock_ima_b(dias=30):
    base_data = datetime.today()
    datas = [(base_data - timedelta(days=i)).date() for i in range(dias)][::-1]
    
    # Criando valores fictícios de índice
    valor_inicial = 3000
    valores = [valor_inicial]
    for _ in range(1, dias):
        variacao = 1 + (0.0005 - 0.001 * np.random.rand())  # Pequena flutuação
        valores.append(valores[-1] * variacao)
    
    df_mock = pd.DataFrame({
        "data_referencia": datas,
        "valor_indice": valores,
        "indice": "IMA_B"
    })
    return df_mock

# 2. Usar os dados mock
df_ima_b = gerar_dados_mock_ima_b(60)  # 60 dias
print(df_ima_b.head())

# 3. Exemplo de visualização
plt.figure(figsize=(10, 5))
plt.plot(df_ima_b["data_referencia"], df_ima_b["valor_indice"], label="IMA-B (mock)")
plt.title("Evolução Simulada do IMA-B")
plt.xlabel("Data")
plt.ylabel("Valor do Índice")
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
