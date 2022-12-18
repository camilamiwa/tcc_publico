import time
start = time.time()

import a04_estatisticas_modelo

import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from imblearn.over_sampling import SMOTE 
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier

import requests

def sugestoes(empresa_positiva, nova, modelo, tipo,
  GLOBAL_URL = 'http://127.0.0.1:5000/', 
  theory_name = 'jocaJ',
  company_cnpj = 'jocaJ'):
    json_to_update = { "$set": {"suggestions_{}".format(tipo): {} }}

    for parametro in empresa_positiva.columns.tolist():
      nova_alterada = nova.copy()
      if float(nova_alterada[parametro][0]) != float(empresa_positiva[parametro][0]):
        dado_original = nova_alterada[parametro]
        nova_alterada[parametro] = empresa_positiva[parametro]
        
        isApproved = modelo.predict(nova_alterada)
        
        if isApproved:
          if empresa_positiva[parametro].dtype != bool:
            aux_max = max(float(dado_original), float(empresa_positiva[parametro]))

            parametro_not_approved = float(dado_original)
            parametro_approved = float(empresa_positiva[parametro])    
            
            diferenca_parametro = parametro_not_approved - parametro_approved   
            
            while abs(diferenca_parametro/aux_max) > 0.05:
              # em no maximo 6 iteracoes, ja tem a diferenca (0.5)^5 = 0.0312
              aux_meio = abs(parametro_not_approved + parametro_approved)/2
              nova_alterada[parametro] = aux_meio            
              intermediario_approved = modelo.predict(nova_alterada)
              
              if intermediario_approved:
                  parametro_approved = aux_meio
              else: parametro_not_approved = aux_meio
                                  
              diferenca_parametro = parametro_not_approved - parametro_approved

            nova_alterada[parametro] = parametro_approved
             
          json_to_update["$set"]["suggestions_{}".format(tipo)]['1param_{}'.format(parametro)] = nova_alterada.to_dict(orient="index")

          print("\n[INFO] {}: Simulacao interessante! Alteracao do parametro: {}".format(tipo, parametro))
          print(nova_alterada)

    parametros = empresa_positiva.columns.tolist()
    for index_parametro in range(len(parametros)):
      nova_alterada = nova.copy()
      if float(nova_alterada[parametros[index_parametro]][0]) != float(empresa_positiva[parametros[index_parametro]][0]):
        nova_alterada[parametros[index_parametro]] = empresa_positiva[parametros[index_parametro]]  
        for second_index in range(index_parametro+1, len(parametros)):
          if float(nova_alterada[parametros[second_index]][0]) != empresa_positiva[parametros[second_index]][0]:
            nova_alterada[parametros[second_index]] = empresa_positiva[parametros[second_index]]  
            isApproved = modelo.predict(nova_alterada)
            
            if isApproved:        
              print("\n[INFO] {}: Simulacao interessante! Alteracao dos parametros: {} e {}".format(
                tipo, parametros[index_parametro], parametros[second_index]))
              print(nova_alterada)
              
              key_to_update = '2param_{}_and_{}'.format(parametros[index_parametro], parametros[second_index])
              json_to_update["$set"]["suggestions_{}".format(tipo)][key_to_update] = nova_alterada.to_dict(orient="index")

            # retorna a mudanca do segundo param
            nova_alterada[parametros[second_index]] = nova[parametros[second_index]] 

    mongo_response = requests.put(GLOBAL_URL + 'results/{}/{}'.format(theory_name, company_cnpj),
        json = json_to_update)  
    if mongo_response.status_code == 200:
      print('\n[INFO] Resultado salvo na base')

    print("\n[INFO] Fim das simulacoes - modelo {}".format(tipo))
  
def analise(X_nova_empresa, historico_positivo, modelo, tipo = "rf",
  GLOBAL_URL = 'http://127.0.0.1:5000/', 
  theory_name = 'jocaJ',
  company_cnpj = 'jocaJ'):
    print("\n[INFO] Iniciando analise da nova empresa - modelo {}".format(tipo))

    print(X_nova_empresa)
    isApproved = modelo.predict(X_nova_empresa)
    print("\n[INFO] INVESTIR!" if isApproved else "\n[INFO] Nao aconselhamos, veja os comentarios!")

    json_to_save = {
        '_company_cnpj': company_cnpj,
        '_theory_name': theory_name,
        'approved': bool(isApproved)
    }

    json_to_update = { "$set": json_to_save }
    mongo_response = requests.put(GLOBAL_URL + 'results/{}/{}'.format(theory_name, company_cnpj),
        json = json_to_update)

    if mongo_response.status_code == 400:
      mongo_response = requests.post(GLOBAL_URL + 'results', json = json_to_save)  

    if mongo_response.status_code == 200:
      print('\n[INFO] Resultado salvo na base')

    if not isApproved:	
      colunas_booleanas = []
      for coluna in X_nova_empresa.columns.tolist():
        if X_nova_empresa[coluna].dtype == bool:
          X_nova_empresa[coluna] = X_nova_empresa[coluna].astype(int)
          historico_positivo[coluna] = historico_positivo[coluna].astype(int)
          colunas_booleanas.append(coluna)    

      to_be_normalized = pd.concat([historico_positivo, X_nova_empresa], ignore_index=True)
      normalized_df=(to_be_normalized-to_be_normalized.min())/(to_be_normalized.max()-to_be_normalized.min())

      X_nova_empresa_normalized = normalized_df.iloc[-1]
      historico_positivo_normalized = normalized_df.drop(normalized_df.tail(1).index)
      sugestao = cdist(historico_positivo_normalized.to_numpy(), [X_nova_empresa_normalized.to_numpy()], metric='cosine')
      sugestao = sugestao.transpose()[0]
      sugestao = np.delete(sugestao, -1)

      for coluna in colunas_booleanas:
        X_nova_empresa[coluna] = X_nova_empresa[coluna].astype(bool)
        historico_positivo[coluna] = historico_positivo[coluna].astype(bool)
            
    while not isApproved:
      index_empresa_similar = np.where(sugestao == sugestao.min())
      empresa_similar = historico_positivo.iloc[index_empresa_similar[0][0]].to_frame().transpose().reset_index(drop=True)

      isApproved = modelo.predict(empresa_similar)

      if not isApproved:
        sugestao = np.delete(sugestao, index_empresa_similar[0][0])   
      else:     
        print('\n[INFO] Proximo teste: o mais proximo esta no indice {} com distancia {}'.format(
          index_empresa_similar[0][0], sugestao.min()))
        print(empresa_similar)
        
        # json_to_update = { "$set": {"suggestions": {} }}
        # mongo_response = requests.put(GLOBAL_URL + 'results/{}/{}'.format(theory_name, company_cnpj),
        #     json = json_to_update)  

        # if mongo_response.status_code == 200:
        #   print('\n[INFO] Sugestoes resetadas na base')
      
        sugestoes(empresa_similar, X_nova_empresa, modelo, tipo, GLOBAL_URL, theory_name, company_cnpj)

def carregar_modelo(GLOBAL_URL, investor_name, theory_name, return_models = True):
  print('[INFO] Carregando modelo, base historica do investidor e dados da empresa')    
  return a04_estatisticas_modelo.main(GLOBAL_URL, investor_name, theory_name, return_models)

def main(GLOBAL_URL = 'http://127.0.0.1:5000/', 
  investor_name = 'jocaJ', theory_name = 'jocaJ',
  current_company = 'jocaJ',
  base_historica = r'bases_csv\03_historico_cinco_params.csv',
  empresa_csv = r'novas_empresas_csv\nova_empresa_01.csv'):
    print('[INFO] Inicio da etapa 05 - Analise da empresa cadastrada')

    knn, rf = carregar_modelo(GLOBAL_URL, investor_name, theory_name)

    # historico = pd.read_csv(base_historica)
    get_from_mongo = requests.get(GLOBAL_URL + 'investors_theory/historic_filtrado/{}/{}'.format(investor_name,theory_name))

    historico = pd.DataFrame.from_dict(get_from_mongo.json()['historic'], orient = 'index')
    
    columns_to_remove = []
    get_from_mongo = requests.get(GLOBAL_URL + 'investors/dtypes')
    columns_dtypes = get_from_mongo.json()['dtypes']
    for key, value in columns_dtypes.items():
      if key in historico.columns.tolist():
        columns_dtypes[key] = np.dtype(value)
      else:
        columns_to_remove.append(key)    
    
    for key in columns_to_remove:
      del columns_dtypes[key]

    historico = historico.astype(dtype = columns_dtypes)
    historico.reset_index(inplace=True, drop = True)

    filter_cols = historico.columns.tolist()
    historico_positivo = historico.loc[historico['Investiu']].copy()
    historico_positivo.drop("Investiu", axis=1, inplace = True)
    
    # X_nova_empresa = pd.read_csv(empresa_csv)

    get_from_mongo = requests.get(GLOBAL_URL + 'company/from_csv/cnpj/{}'.format(current_company))

    X_nova_empresa = pd.DataFrame.from_dict(get_from_mongo.json()['company_data'], orient = 'index')
    
    columns_to_remove = []
    get_from_mongo = requests.get(GLOBAL_URL + 'investors/dtypes')
    columns_dtypes = get_from_mongo.json()['dtypes']
    for key, value in columns_dtypes.items():
      if key in X_nova_empresa.columns.tolist():
        columns_dtypes[key] = np.dtype(value)
      else:
        columns_to_remove.append(key)    
    
    for key in columns_to_remove:
      del columns_dtypes[key]

    X_nova_empresa = X_nova_empresa.astype(dtype = columns_dtypes)
    X_nova_empresa.reset_index(inplace=True, drop = True)


    for coluna in X_nova_empresa.columns.tolist():
      if coluna not in filter_cols:
        X_nova_empresa.drop(coluna, axis=1, inplace=True)   

    analise(X_nova_empresa, historico_positivo, knn, "knn", GLOBAL_URL, theory_name, current_company) 
    analise(X_nova_empresa, historico_positivo, rf, "rf", GLOBAL_URL, theory_name, current_company) 

    end = time.time()
    print('[SUCCESS] Fim da etapa 05. Durou: {} segundos'.format(round(end-start, 3)))

if __name__ == "__main__":
  main()