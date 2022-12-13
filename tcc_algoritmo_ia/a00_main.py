import time
start_total = time.time()

import a01_sintese_preparacao_dados
import a02_tratamento_dados
import a03_filtro_parametros
# import a04_estatisticas_modelo
import a05_analise_nova_empresa

seed = 10
noise = 2

GLOBAL_URL = 'http://127.0.0.1:5000/'
IS_SHOWING_DETAILS = False

investor_name = 'jocaJ'
current_user = investor_name
theory_name = investor_name
current_company = 'jocaJ'

file_name_01 = r'bases_csv\01_historico_base_crua.csv'
base_analisadas_manual = r'bases_para_analise\analisadas.csv'
tese_exemplo = r'bases_para_analise\Tese_Investimento_Exemplo.csv'
file_name_02 = r'bases_csv\02_historico_tratado.csv'
many_file_name_03 = {
  'automatizado': r'bases_csv\03_historico_otimizado_doze_cols.csv',
  'manual': r'bases_csv\03_historico_cinco_params.csv'
}
file_name_03 = many_file_name_03['manual']
filtro_parametros_03 = {'manual': 6}
return_models = False
model_file_name_04 = {
  'knn': r'modelos\knn_pickle_file',
  'rf': r'modelos\rf_pickle_file'
}
empresa_csv = r'novas_empresas_csv\nova_empresa_02.csv'

a01_sintese_preparacao_dados.main(file_name_01, base_analisadas_manual, tese_exemplo, IS_SHOWING_DETAILS, noise, seed,
  GLOBAL_URL, investor_name, theory_name)
a02_tratamento_dados.main(file_name_01, file_name_02, GLOBAL_URL, investor_name, theory_name)
a03_filtro_parametros.main(file_name_02, many_file_name_03, IS_SHOWING_DETAILS, seed, filtro_parametros_03,
  GLOBAL_URL, investor_name, theory_name)
# a04_estatisticas_modelo.main(GLOBAL_URL, investor_name, theory_name, return_models, seed, file_name_03, model_file_name_04)
a05_analise_nova_empresa.main(GLOBAL_URL, investor_name, theory_name, current_company)

end_total = time.time()
print('[SUCCESS] Finalizou todas as etapas! Durou: {} segundos'.format(round(end_total-start_total, 3)))