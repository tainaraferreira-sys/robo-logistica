import pandas as pd
import requests
import json
import os

# CONFIGURAÇÕES
SESSION_ID = os.getenv("METABASE_SESSION") # Pegará do GitHub Secrets
URL_BASE = "https://metabase.gobeaute.com.br/api"
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1Oh-3Pa5Bz02eQazMDcjI3bO1emc_O0FCqHcQ9s1DB6w/export?format=csv"

headers = {"X-Metabase-Session": SESSION_ID}

def get_data(card_id):
    r = requests.post(f"{URL_BASE}/card/{card_id}/query/json", headers=headers)
    return pd.DataFrame(r.json())

# 1. Carregar Dados
df_nfs = pd.read_csv(URL_PLANILHA)
df_pedidos = get_data(18417)
df_estoque = get_data(17988)
df_cadastro = get_data(18867) # Cadastro EAN/SKU

# 2. Preparar Dados
df_nfs['Data Emissão'] = pd.to_datetime(df_nfs['Data Emissão'], dayfirst=True)
df_nfs = df_nfs.sort_values('Data Emissão') # FIFO
ean_to_sku = dict(zip(df_cadastro['ean'], df_cadastro['sku']))

# 3. Lógica de Conciliação
resultados = []
for _, nf in df_nfs.iterrows():
    sku = ean_to_sku.get(nf['EAN'])
    preco_nf = round(float(nf['Preço Unit.']), 2)
    
    # Filtro rígido: SKU igual + Preço igual + Tem Saldo
    pedido = df_pedidos[
        (df_pedidos['cod_produto'] == sku) & 
        (df_pedidos['valor_unitario'].round(2) == preco_nf) & 
        (df_pedidos['saldo_pedido'] > 0)
    ].head(1)

    if not pedido.empty:
        idx = pedido.index[0]
        df_pedidos.at[idx, 'saldo_pedido'] -= nf['Quantidade'] # Consome saldo
        status = "OK - Pedido Vinculado"
    else:
        status = "Divergência de Preço ou Sem Saldo"
        
    resultados.append({"nf": nf['NumeroNF'], "status": status, "sku": sku})

# 4. Salvar para o Netlify
with open('dados_conciliados.json', 'w') as f:
    json.dump(resultados, f)
