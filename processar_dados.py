import pandas as pd
import requests
import json
import os

# IDs das perguntas do Metabase
IDS = {"pedidos": 18417, "estoque": 17988, "pagamentos": 18752}

SESSION_ID = os.getenv("METABASE_SESSION")
URL_BASE = "https://metabase.gobeaute.com.br/api"

# Suas planilhas do Google
URL_PLANILHA_NFS = "https://docs.google.com/spreadsheets/d/1Oh-3Pa5Bz02eQazMDcjI3bO1emc_O0FCqHcQ9s1DB6w/export?format=csv"
URL_PLANILHA_CADASTRO = "https://docs.google.com/spreadsheets/d/1Ma2ynNyv0nNzLU58lVq0R9LKwEGbYr2Pkrbq3V5GB94/export?format=csv&gid=1201360779"

headers = {"X-Metabase-Session": SESSION_ID}

def get_metabase_data(card_id):
    try:
        response = requests.post(f"{URL_BASE}/card/{card_id}/query/json", headers=headers)
        df = pd.DataFrame(response.json())
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df
    except Exception as e:
        print(f"Erro no Metabase Card {card_id}: {e}")
        return pd.DataFrame()

# 1. Carregar Bases de Dados
print("Carregando planilhas e Metabase...")
df_nfs = pd.read_csv(URL_PLANILHA_NFS)
df_nfs.columns = [str(c).lower().strip() for c in df_nfs.columns]

df_cadastro = pd.read_csv(URL_PLANILHA_CADASTRO)
df_cadastro.columns = [str(c).lower().strip() for c in df_cadastro.columns]

df_pedidos = get_metabase_data(IDS["pedidos"])
df_estoque = get_metabase_data(IDS["estoque"])

# 2. Criar Dicionário de Tradução (EAN -> SKU)
# Ajustado para usar as colunas da sua planilha de cadastro
ean_to_sku = dict(zip(df_cadastro['ean'].astype(str), df_cadastro['sku'].astype(str)))

# 3. Lógica FIFO e Conciliação
if 'data emissão' in df_nfs.columns:
    df_nfs['data emissão'] = pd.to_datetime(df_nfs['data emissão'], dayfirst=True, errors='coerce')
    df_nfs = df_nfs.sort_values('data emissão')

relatorio_final = []

print("Cruzando dados...")
for _, nf in df_nfs.iterrows():
    # Pega o EAN da nota e descobre o SKU
    ean_nf = str(nf.get('ean', '')).strip()
    sku = ean_to_sku.get(ean_nf)
    
    # Preço e Quantidade
    col_preco = [c for c in df_nfs.columns if 'preço' in c or 'preco' in c][0]
    preco_nf = round(float(nf[col_preco]), 2)
    qtd_nf = float(nf.get('quantidade', 0))
    
    status_ped = "SKU NÃO ENCONTRADO NO CADASTRO"
    num_ped = "N/A"

    if sku:
        # Filtro: SKU igual + Preço idêntico + Tem Saldo
        pedidos_validos = df_pedidos[
            (df_pedidos['cod_produto'].astype(str) == sku) & 
            (df_pedidos['valor_unitario'].astype(float).round(2) == preco_nf) & 
            (df_pedidos['saldo_pedido'].astype(float) > 0)
        ]

        if not pedidos_validos.empty:
            idx = pedidos_validos.index[0]
            if df_pedidos.at[idx, 'saldo_pedido'] >= qtd_nf:
                df_pedidos.at[idx, 'saldo_pedido'] -= qtd_nf
                status_ped = "PEDIDO OK"
                num_ped = pedidos_validos.at[idx, 'num_pedido']
            else:
                status_ped = "SALDO INSUFICIENTE (FIFO)"
        else:
            status_ped = "DIVERGÊNCIA DE PREÇO OU SEM PEDIDO"

    # Verifica se já foi lançada (Estoque)
    nf_num = str(nf.get('numeronf', ''))
    foi_lancada = not df_estoque[df_estoque['nota_fiscal'].astype(str) == nf_num].empty

    relatorio_final.append({
        "nf": nf_num,
        "sku": sku,
        "ean": ean_nf,
        "status_pedido": status_ped,
        "pedido_protheus": num_ped,
        "foi_lancada": "SIM" if foi_lancada else "NÃO"
    })

# 4. Salvar Resultado
with open('dados_conciliados.json', 'w', encoding='utf-8') as f:
    json.dump(relatorio_final, f, indent=4, ensure_ascii=False)

print("Processo concluído com sucesso!")
