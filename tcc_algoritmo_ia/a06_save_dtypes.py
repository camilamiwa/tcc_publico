import requests
import pandas as pd
import numpy as np
import json

GLOBAL_URL = 'http://127.0.0.1:5000/'

dtypes_pandas = pd.read_csv(r"bases_para_analise\Tese_Investimento_Exemplo.csv")

# dtypes_pandas.rename(
#         columns={'Nome da empresa':'Nome_empresa',          # passando o nome antigo e novo como um dicionário
#                 'Data da submissão':'Data_submissao',
#                 'Data de fundação': 'Data_fundacao',
#                 'Quantidade de funcionários':'Quantidade_funcionarios',
#                 'Indústria': 'Industria',
#                 'Produto próprio?': 'Produto_proprio',
#                 'Gerando receita?': 'Gerando_receita',
#                 'Receita mensal (R$/mês)':'Receita_mensal',
#                 'Número de Clientes':'Numero_clientes',
#                 'Clientes Recorrentes?':'Clientes_recorrentes',
#                 'CAC histórico (R$)':'CAC_historico',
#                 'Curso Founder':'Curso_Founder',
#                 'Data Decisão':'Data_decisao',
#                 'Investiu?': 'Investiu'
#                 },
#         inplace = True              # para alterar o objeto Panda _tese_, e não criar uma cópia
#     )

cols = (list(dtypes_pandas.columns))
a = list(dtypes_pandas.dtypes)
b = [str(val) for val in a]
dtypes = dict(zip(
    cols,
    b
))

dtypes_values = {
    'dtypes': dtypes,
    'id': 'dtypes_raw'
}

get_from_mongo = requests.post(GLOBAL_URL + 'investors/dtypes', json = dtypes_values)



# import pdb
# pdb.set_trace()

# get_from_mongo = requests.get(GLOBAL_URL + 'investors/dtypes')
# columns_dtypes = get_from_mongo.json()['dtypes']
# for key, value in columns_dtypes.items():
#     columns_dtypes[key] = np.dtype(value)

# import pdb
# pdb.set_trace()
