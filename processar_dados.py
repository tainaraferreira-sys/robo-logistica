import pandas as pd
import requests
import json
import os

# Identificadores das perguntas do Metabase
IDS = {
    "pedidos": 18417,
    "estoque": 17988,
    "pagamentos": 18752,
    "cadastro": 18867
}

SESSION_ID = os.getenv("METABASE_SESSION")
URL_BASE = "https://metabase.gobeaute.com.br/api"
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1Oh-3Pa5Bz02eQazMDcjI3bO1emc_O0FCqHcQ9s1DB6w/export?format=csv"

headers = {"X-Metabase-Session": SESSION_ID}

def get_metabase_data(card_id):
    response = requests.post(f"{URL_BASE}/card/{card_id}/query/json", headers=headers)
    return pd.DataFrame(response.json())

# 1. Carregar todas as bases
df_nfs = pd.read_csv(URL_PLANILHA)
df_pedidos = get_metabase_data(IDS["pedidos"])
df_estoque = get_metabase_data(IDS["estoque"])
df_pagamentos = get_metabase_data(IDS["pagamentos"])
df_cadastro = get_metabase_data(IDS["cadastro"])

# 2. Preparação
df_nfs['Data Emissão'] = pd.to_datetime(df_nfs['Data Emissão'], dayfirst=True)
df_nfs = df_nfs.sort_values('Data Emissão') # Regra FIFO: Antigas primeiro
ean_to_sku = dict(zip(df_cadastro['ean'], df_cadastro['sku']))

# 3. Processamento
relatorio_final = []

for _, nf in df_nfs.iterrows():
    sku = ean_to_sku.get(nf['EAN'])
    preco_nf = round(float(nf['Preço Unit.']), 2)
    
    # Busca pedidos com SKU igual, Preço idêntico e Saldo > 0
    pedidos_validos = df_pedidos[
        (df_pedidos['cod_produto'] == sku) & 
        (df_pedidos['valor_unitario'].round(2) == preco_nf) & 
        (df_pedidos['saldo_pedido'] > 0)
    ]

    status_ped = "SEM PEDIDO / PREÇO DIVERGENTE"
    num_ped = "N/A"

    if not pedidos_validos.empty:
        idx = pedidos_validos.index[0]
        qtd_nf = nf['Quantidade']
        saldo_disponivel = df_pedidos.at[idx, 'saldo_pedido']
        
        if saldo_disponivel >= qtd_nf:
            df_pedidos.at[idx, 'saldo_pedido'] -= qtd_nf # Abate o saldo (FIFO)
            status_ped = "PEDIDO OK"
            num_ped = df_pedidos.at[idx, 'num_pedido']
        else:
            status_ped = "SALDO INSUFICIENTE NO PEDIDO"

    # Verifica se já foi lançada no estoque
    foi_lancada = not df_estoque[df_estoque['nota_fiscal'] == str(nf['NumeroNF'])].empty
    
    # Verifica status de pagamento
    pgto = df_pagamentos[df_pagamentos['nota'] == str(nf['NumeroNF'])].head(1)
    status_pgto = pgto['status_nota'].values[0] if not pgto.empty else "NÃO ENCONTRADO"

    relatorio_final.append({
        "nf": nf['NumeroNF'],
        "sku": sku,
        "status_pedido": status_ped,
        "pedido_origem": num_ped,
        "lancada": "SIM" if foi_lancada else "NÃO",
        "pagamento": status_pgto
    })

# 4. Salva o JSON para o Netlify ler
with open('dados_conciliados.json', 'w') as f:
    json.dump(relatorio_final, f, indent=4)
