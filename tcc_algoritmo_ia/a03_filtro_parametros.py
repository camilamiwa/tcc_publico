"""### 5.2 Seleção das variáveis mais explicativas

Uma etapa importante do processo de análise de dados, também consiste em avaliar as
variáveis disponíveis e o quanto elas contribuem para a decisão.
"""

import time
start = time.time()
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFECV
import matplotlib.pyplot as plt # Bibliotecas para criar os gráficos
import seaborn as sns           # Bibliotecas para criar os gráficos

import requests
import numpy as np

def main(start_file_name = r'bases_csv\02_historico_tratado.csv',
  final_file_names = {'automatizado': r'bases_csv\03_historico_otimizado_doze_cols.csv',
  'manual': r'bases_csv\03_historico_cinco_params.csv'},
  isPlotting = False, seed = 10,
  quantidade_parametros = {'manual': 6},
  GLOBAL_URL = 'http://127.0.0.1:5000/', 
  current_user = 'jocaJ', theory_name = 'jocaJ'):
    print('[INFO] Inicio da etapa 03 - Otimizacao e filtragem dos parametros')

    # historico = pd.read_csv(start_file_name)
    
    get_from_mongo = requests.get(GLOBAL_URL + 'investors_theory/historic_tratado/{}/{}'.format(current_user,theory_name))

    historico = pd.DataFrame.from_dict(get_from_mongo.json()['historic_tratado'], orient = 'index')
    
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

    print('[INFO] Correlacao das variaveis')
    if isPlotting:
      print(historico.corr())
    #Como as variáveis estão correlacionadas com a nossa variável alvo - INVESTIU?
    print('[INFO] Correlacao das variaveis com a variavel investiu')
    correlacoes_investiu = historico.corr()['Investiu']
    if 'manual' in quantidade_parametros.keys():
      correlacoes_investiu = correlacoes_investiu.nlargest(quantidade_parametros['manual'])
    colunas_correlacoes_investiu = correlacoes_investiu.keys().tolist()

    # Também, ao invés de printar no console, pode-se montar um gráfico para analisarmos essas relações de uma maneira mais visual:

    if isPlotting:
        plt.figure(figsize=(10,10))
        sns.heatmap(historico.corr(),annot=True, fmt=".2f", linewidth=.5)
        plt.show()

    # Base com as variáveis explicativas do modelo
    X = historico.drop('Investiu', axis=1)

    # Variavel resposta do modelo 
    y = historico['Investiu']

    # Definição do modelo utilizado
    modelo = RandomForestClassifier(random_state=seed)

    # Aplicação do Algoritmo de Eliminação Recursiva de Variaveis
    selector = RFECV( modelo      # Algoritmo utilizado
                    ,step=1      # Número de variáveis eliminadas por iteração
                    ,cv=5        # Número de grupos no cross validation
                    )

    # Aplicação do Algoritmo 
    #   - O algoritmo iniciara com o treino utilizando todas as variáveis
    #   - A cada etapa será avaliada a importância de cada variável
    #   - A cada iteração as n variáveis menos explicativas (n definido pelo parametro step) são eliminadas
    #   - Por fim, avalia-se em qual iteração (cesta de variáveis) obteve-se a melhor performance 
    #     (pode-se definir a métrica a ser considerada)

    selector = selector.fit(X,y)

    # Resultados no ponto ótimo da curva
    print("Número ótimo de variáveis : %d" % selector.n_features_)
    print("Variáveis Selecionadas :")
    print(X.columns[selector.support_].tolist())

    # Curva de desempenho
    if isPlotting:
        plt.figure()
        plt.xlabel("Número de variáveis analisadas")
        plt.ylabel("Cross validation score")
        plt.plot(range(1, len(selector.grid_scores_) + 1), selector.grid_scores_)
        plt.show()

    """Portanto, carregaremos ao conjunto final, apenas as variáveis selecionadas:"""

    variaveis_orig = X.columns.tolist()
    variaveis_manter = X.columns[selector.support_].tolist()

    X_cinco_params = historico.copy()
    for coluna in variaveis_orig:
      if coluna not in colunas_correlacoes_investiu:
        X_cinco_params.drop(coluna, axis=1, inplace=True)

    if 'manual' in final_file_names.keys():
      print('[INFO] Salvando base crua de dados historicos com cinco parametros em {}'.format(final_file_names['manual']))
      # X_cinco_params.to_csv(final_file_names['manual'], index = False)

    for coluna in variaveis_orig:
      if coluna not in variaveis_manter:
        historico.drop(coluna, axis=1, inplace=True)
    
    if 'automatizado' in final_file_names.keys():
      print('[INFO] Salvando base crua otimizada de dados historicos em {}'.format(final_file_names['automatizado']))
      # historico.to_csv(final_file_names['automatizado'], index = False)    

    json_to_save = {
      '_user_name': current_user,
      '_theory_name': theory_name
    }
    if 'completo' in theory_name:
      json_to_save['historic'] = historico.to_dict(orient="index")
    else:      
      json_to_save['historic'] = X_cinco_params.to_dict(orient="index")

    json_to_update = { "$set": json_to_save }
    mongo_response = requests.put(GLOBAL_URL + 'investors_theory/historic_filtrado/{}/{}'.format(current_user,theory_name),
        json = json_to_update)

    if mongo_response.status_code == 400:
      mongo_response = requests.post(GLOBAL_URL + 'investors_theory/historic_filtrado', json = json_to_save)

    if mongo_response.status_code == 200:
      print('[SUCCESS] Fase 3 - Salvou dados no mongo')
    
    end = time.time()
    print('[SUCCESS] Fim da etapa 03. Durou: {} segundos'.format(round(end-start, 3)))

if __name__ == "__main__":
    main()