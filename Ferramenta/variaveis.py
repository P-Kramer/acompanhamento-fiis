import pandas as pd
from datetime import datetime
import streamlit as st

# Caminho para seu arquivo Excel
arquivo = r"C:\Users\User\Documents\OneDrive\Documentos\Guilherme\Precos_Reuters.xlsm"

# Lê a aba "Variáveis"
df_variaveis = pd.read_excel(arquivo, sheet_name="Variaveis")

