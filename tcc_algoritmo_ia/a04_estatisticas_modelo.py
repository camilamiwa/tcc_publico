import time
start = time.time()

import pandas as pd
import pickle
from imblearn.over_sampling import SMOTE 
from sklearn.model_selection import train_test_split  # Método de separação dos conjuntos de Treino, Validação e Teste
from sklearn.model_selection import GridSearchCV      # Método de seleção dos parâmetros mais explicativos
from sklearn.neighbors import KNeighborsClassifier     # Modelo Classifier de Análise
from sklearn.neighbors import KNeighborsRegressor     # Modelo Regressor de Análise
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (explained_variance_score, # Métricas de avaliação do modelo
                             mean_absolute_error, 
                             mean_squared_error, 
                             mean_squared_log_error,
                             r2_score,
                             confusion_matrix,
                             classification_report,
                             roc_auc_score)
 
import requests
import numpy as np

"""### 5.2 Seleção das variáveis mais explicativas

Uma etapa importante do processo de análise de dados, também consiste em avaliar as
variáveis disponíveis e o quanto elas contribuem para a decisão.
"""

def main(GLOBAL_URL = 'http://127.0.0.1:5000/', 
  investor_name = 'jocaJ', theory_name = 'jocaJ',
  return_models = False, seed = 10,
  start_file_name = r'bases_csv\03_historico_cinco_params.csv',
  model_file_name = {'knn': r'modelos\knn_pickle_file',
  'rf': r'modelos\rf_pickle_file'}):
    print('[INFO] Inicio da etapa 04 - Definicao e treino do modelo')

    # historico = pd.read_csv(start_file_name)

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

    y_pre_oversampling = historico.Investiu
    X_pre_oversampling = historico.drop("Investiu", axis=1)

    print('[INFO] Oversampling para balancear positivos e negativos')
    # Oversampling, para balancear positivos e negativos
    # Os resultados de recall positivo aumentou de 0.3 para 0.87
    sm = SMOTE(random_state=seed)
    X, y = sm.fit_resample(X_pre_oversampling, y_pre_oversampling)

    """## 6. Treino dos modelos

    ### 6.1. Separação dos conjuntos de dados - Treino, Validação e Teste

    Antes de aplicar e treinar o modelo, precisamos separar o conjunto de dados em conjunto de Treino, Validação e Teste.

    - **X_test** e **y_test**: conjunto de teste (vermelho)
    - **X_training** e **y_training**: conjunto auxiliar de treino (verde superior) para o método de holdout (com validação cruzada)
    - **X_train** e **y_train**: conjunto de treino (verde inferior) para treino sem validação cruzada
    - **X_val** e **y_val**: conjunto de validação (amarelo) para avaliar os modelos sem validação cruzada

    <img src="https://cdn-images-1.medium.com/max/1200/1*4G__SV580CxFj78o9yUXuQ.png" alt="cv" style="width: 300px; height: 200px"/>
    """

    print('[INFO] Divisao da base para treino, validacao e teste')
    # Primeiro, é feita a separação do conjunto de TESTE
    X_training, X_test, y_training, y_test = train_test_split(X, y, random_state=seed, test_size=0.25)

    # # Em seguida, separamos o conjunto que sobrou nos dados de VALIDAÇÃO e TREINO
    X_train, X_val, y_train, y_val = train_test_split(X_training, y_training, random_state=seed, test_size=0.33)

    """Tendo os conjuntos devidamente separados, agora pode-se avançar para o treino dos modelos: `K-Nearest Neighbours` e `Random Forest`.

    ### 6.2 Hiperparâmetros Modelo K-Nearest Neighbours

    Cada tipo de algoritmo de Machine Learning, exige parâmetros que são genéricos e não dependem do problema
    específico que está sendo resolvido - são esses, os hiperparâmetros. Para **K-Nearest Neighbours**,
    podemos fazer um estudo para definir os melhores hiperparâmetros - aqueles que não são as variáveis do modelo.
    A seguir, usaremos o método `GridSearchCV` para tal tarefa.

    Este método nos permite fazer tanto a **busca pelos melhores hiperparâmetros** quanto também a **validação cruzada** do modelo.
    """

    print('\n[INFO] Otimizacao de hiperparametros para o KNN')
    # Hiper-Parâmetros a serem testados
    params = {'n_neighbors': range(2, 51),
              'weights': ['uniform', 'distance']}
    
    # knn = KNeighborsRegressor()
    knn = KNeighborsClassifier()

    grid_search_knn = GridSearchCV(knn, param_grid=params, return_train_score=True) 

    grid_search_knn.fit(X_training, y_training)

    print('Melhores hiperparametros: {}'.format(grid_search_knn.best_params_))
    print('Score da base de treino: {:.3f}'.format(grid_search_knn.score(X_training, y_training)))

    # A aplicacao do modelo ficará mais para o final, para não "travar" no meio do código

    """### 6.3 Hiperparâmetros Modelo Random Forest"""

    print('\n[INFO] Otimizacao de hiperparametros para o Random Forest')
    # Hiper-Parâmetros a serem testados                             
    params = {'n_estimators': range(10, 101, 5)}

    rf = RandomForestClassifier()

    grid_search_rf = GridSearchCV(rf, param_grid=params, return_train_score=True) 

    grid_search_rf.fit(X_training, y_training)

    print('Melhores hiperparametros: {}'.format(grid_search_rf.best_params_))
    print('Score da base de treino: {:.3f}'.format(grid_search_rf.score(X_training, y_training)))

    """### 6.4 Aplicação dos modelos nos grupos de treinamento"""

    """O modelo K-Nearest Neighbours pode atender tanto problemas de classificação quanto de regressão, este último é o nosso caso.

    [Referência do modelo](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsRegressor.html)
    """

    print('\n[INFO] Treino dos modelos')
    # configurando o modelo com a melhor combinação de hiperparâmetros
    knn.set_params(n_neighbors = grid_search_knn.best_params_['n_neighbors'],
                  weights = grid_search_knn.best_params_['weights'])

    knn.fit(X_train, y_train)

    # configurando o modelo com a melhor combinação de hiperparâmetros
    rf.set_params(n_estimators = grid_search_rf.best_params_['n_estimators'])

    rf.fit(X_train, y_train)

    """## 7. Aplicação do modelo

    # Feito o fitting, para a aplicação basta usar o método `predict` para cada um dos modelos
    # """

    if return_models:
      print('[INFO] Retornando modelos')
      end = time.time()
      print('[SUCCESS] Fim da etapa 04. Durou: {} segundos'.format(round(end-start, 3)))

      return knn, rf

    else:
      y_pred_knn = knn.predict(X_test)
      y_pred_rf = rf.predict(X_test)

      """Agora, podemos analisar os resultados dessa predição e avaliar sua eficiência"""

      # CLASSIFICAÇÃO
      print("[INFO] Estatisticas com conjunto de teste modelo KNN")
      print("Acuracia no conjunto de treino: {:.3f}".format(knn.score(X_train, y_train)))
      print("Acuracia no conjunto de teste: {:.3f}".format(knn.score(X_test, y_test)))
      print("Area sob a curva ROC: {:.3f}".format(roc_auc_score(y_test, y_pred_knn)))
      print("Matriz de confusao:")
      print(confusion_matrix(y_test, y_pred_knn))
      print("Relatorio do modelo:")
      print(classification_report(y_test, y_pred_knn))

      print("[INFO] Estatisticas com conjunto de teste modelo rf")
      print("Acuracia no conjunto de treino: {:.3f}".format(rf.score(X_train, y_train)))
      print("Acuracia no conjunto de teste: {:.3f}".format(rf.score(X_test, y_test)))
      print("Area sob a curva ROC: {:.3f}".format(roc_auc_score(y_test, y_pred_rf)))
      print("Matriz de confusao:")
      print(confusion_matrix(y_test, y_pred_rf))
      print("Relatorio do modelo:")
      print(classification_report(y_test, y_pred_rf))

      print('\n[INFO] Validacao dos modelos')
      y_pred_knn = knn.predict(X_val)
      y_pred_rf = rf.predict(X_val)

      """Agora, podemos analisar os resultados dessa predição e avaliar sua eficiência"""

      # CLASSIFICAÇÃO
      print("[INFO] Validacao do modelo KNN")
      print("Acuracia no conjunto de validacao: {:.3f}".format(knn.score(X_val, y_val)))
      print("Area sob a curva ROC: {:.3f}".format(roc_auc_score(y_val, y_pred_knn)))
      # Matriz de confusão:
      # Verdadeiros Negativos | Falsos Positivos
      # Falsos Negativos | Verdadeiros Positivos
      print("Matriz de confusao:")
      print(confusion_matrix(y_val, y_pred_knn))
      print("Relatorio do modelo:")
      print(classification_report(y_val, y_pred_knn))

      print("[INFO] Validacao do modelo rf")
      print("Acuracia no conjunto de validacao: {:.3f}".format(rf.score(X_val, y_val)))
      print("Area sob a curva ROC: {:.3f}".format(roc_auc_score(y_val, y_pred_rf)))
      print("Matriz de confusao:")
      print(confusion_matrix(y_val, y_pred_rf))
      print("Relatorio do modelo:")
      print(classification_report(y_val, y_pred_rf))
      
      end = time.time()
      print('[SUCCESS] Fim da etapa 04. Durou: {} segundos'.format(round(end-start, 3)))

          
    # print('\n[INFO] Salvando modelos em arquivos pickle')
    # # Save the trained model as a pickle string.
    # knnPickle = open(model_file_name['knn'], 'wb')           
    # # source, destination 
    # pickle.dump(knn, knnPickle)  
    # # close the file
    # knnPickle.close()

    # rfPickle = open(model_file_name['rf'], 'wb') 
    # pickle.dump(rf, rfPickle)  
    # rfPickle.close()
    

if __name__ == "__main__":
    main()