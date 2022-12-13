# -*- coding: utf-8 -*-
"""
Original file is located at
    https://colab.research.google.com/drive/1QOOMZYB7svU_UT-OALLdFoeC9yP_0h2O
"""

import time
start = time.time()

import pandas as pd             # Utilização da estrutura DataFrame, muito conveniente para a manipulação de conjuntos de dados
from datetime import datetime   # Tipo de variável de data

import sklearn.datasets as dt   # Para ampliar o conjunto de dados 
from sklearn import preprocessing  # Para redimensionar o conjunto de dados

import matplotlib.pyplot as plt # Bibliotecas para criar os gráficos
import seaborn as sns           # Bibliotecas para criar os gráficos

import requests

def main(final_file_name = r'bases_csv\01_historico_base_crua.csv',
  base_analisadas_manual = r'bases_csv\analisadas.csv',
  tese_exemplo = r'bases_csv\Tese_Investimento_Exemplo.csv',
  IS_GRAPH_ACTIVE = False, noise = 2, seed = 10,
  IS_MANUAL_ANALYSIS_DONE = True,
  GLOBAL_URL = 'http://127.0.0.1:5000/', 
  current_user = 'jocaJ', theory_name = 'jocaJ'):
    print('[INFO] Inicio da etapa 01 - Sintese e preparacao dos dados')
    print('[INFO] Leitura do csv de base')

    #if (tese_exemplo == 'bases_csv\Tese_Investimento_Exemplo.csv'):
     # tese = pd.read_csv(tese_exemplo)
    tese = tese_exemplo
    X_synth, y_synth = dt.make_regression(n_samples=1000,
                                          n_features=14,
                                          n_informative = 14,
                                          noise=noise,
                                          random_state=seed
                                          )

    df_synth = pd.DataFrame(data = X_synth, columns = tese.columns)
    print('[INFO] Síntese de dados para aumentar a base')
    
    # Primeiro passo é normalizar a distribuição de dados sintéticos para o intervalo de 0 a 1
    scaler = preprocessing.MinMaxScaler()
    scaled_df = scaler.fit_transform(df_synth)
    scaled_df = pd.DataFrame(data = scaled_df, columns=tese.columns)
    print('[INFO] Normalizacao dos dados sintetizados')

    if IS_GRAPH_ACTIVE:
      fig, (ax1, ax2) = plt.subplots(ncols=2)
      # Conferir se deu certo a partir da variável 'Quantidade de funcionários'
      ax1.set_title('Pré-Normalização')
      sns.kdeplot(df_synth['Quantidade de funcionários'], ax=ax1)
      ax2.set_title('Pós-Normalização')
      sns.kdeplot(scaled_df['Quantidade de funcionários'], ax=ax2)
    
    # As datas temos que manipular para o formato DateTime
    for i in ("Data da submissão", "Data de fundação", "Data Decisão"):
      # Passando as datas reais fornecidas para o formato ISO
      data_sub = tese[i].str[-4::] + "-" + tese[i].str[3:5] + "-" + tese[i].str[0:2]
      data_sub = data_sub.map(datetime.fromisoformat)
      # Convertendo-as para números ordinais
      data_sub = data_sub.apply(lambda x: x.toordinal())

      # Alterando a escala dos dados sintéticos com base nas datas da tese
      scaler2 = preprocessing.MinMaxScaler(feature_range=(data_sub.min(), data_sub.max()))
      data_corrig = scaler2.fit_transform(scaled_df[[i]])
      data_corrig = data_corrig.round()
      scaled_df[i] = data_corrig

      # Retornando à formatação de datas do padrão DateTime (YYYY-MM-DD)
      scaled_df[i] = scaled_df[i].apply(lambda x: datetime.fromordinal(int(x)))
      # Retornando à formatação de datas do padrão brasileiro entendido como input do usuário (DD-MM-YYYY)
      scaled_df[i] = scaled_df[i].apply(lambda x: str(x.day) + "/" + str(x.month) + "/" + str(x.year))

    print('[INFO] Tratamento e normalizacao de datas com datetime')
    
    for i in ('Quantidade de funcionários', 'Receita mensal (R$/mês)','Número de Clientes', 'CAC histórico (R$)'):
      # Alterando a escala dos dados sintéticos com base nos dados da tese
      scaler3 = preprocessing.MinMaxScaler(feature_range=(tese[i].min(), tese[i].max()))
      dados_escal = scaler3.fit_transform(scaled_df[[i]])
      dados_escal = dados_escal.round()
      scaled_df[i] = dados_escal

    print('[INFO] Tratamento e normalizacao de colunas numéricas')
    
    # Para as seguintes variáveis podemos fazer um corte seco e converter diretamente
    scaled_df['Produto próprio?']       = scaled_df['Produto próprio?'].apply(lambda x: "Sim" if x > 0.5 else "Não")
    scaled_df['Clientes Recorrentes?']  = scaled_df['Clientes Recorrentes?'].apply(lambda x: "Sim" if x > 0.5 else "Não")
    # Miwa comentario: aqui nao precisa da linha abaixo, ja que essa coluna terá o valor definido não aleatoriamente
    # Miwa comentario: talvez para "deixar mas realista", aumentar o threshold de 0.5 para 0.7 por exemplo
    scaled_df['Investiu?']              = scaled_df['Investiu?'].apply(lambda x: "Sim" if x > 0.5 else "Não")

    # A variável 'Gerando receita?' depende da variável 'Receita Mensal (R$/Mês)'
    quartil_25 = scaled_df['Gerando receita?'].quantile(0.25)
    scaled_df['Gerando receita?'] = scaled_df['Gerando receita?'].apply(lambda x: "Sim" if x > quartil_25 else "Não")

    # Para manter a consistência no DataSet, alteraremos a 'Receita Mensal (R$/Mês)' também
    scaled_df['Receita mensal (R$/mês)'] = scaled_df.apply(lambda x: 0 if x['Gerando receita?'] == "Não" else x['Receita mensal (R$/mês)'], axis = 1)

    """Finalmente, as últimas variáveis faltantes para adaptar ao contexto de análise de empresas são as
    `{Indústria, Curso Founder}`. Como são rótulos, recolheremos os valores presentes na tese e distribuiremos 
    na base sintética a partir de bins."""

    if IS_GRAPH_ACTIVE:
      scaled_df['Indústria'].hist()
      scaled_df['Curso Founder'].hist()

    # Criando as listas a partir da tese
    inds = tese['Indústria'].unique()
    cursos = tese['Curso Founder'].unique()

    # Como as variáveis sintéticas são de 0 a 1, multiplicamos pelo tamanho da lista e arredondamos para pegar o índice mais próximo
    scaled_df['Indústria'] = scaled_df['Indústria'].apply(lambda x: inds[round(x * (len(inds)-1))])
    scaled_df['Curso Founder'] = scaled_df['Curso Founder'].apply(lambda x: cursos[round(x* (len(cursos)-1))])

    print('[INFO] "Traduzindo" valores numéricos em valores qualitativos')
    if IS_GRAPH_ACTIVE:
      scaled_df['Indústria'].value_counts()
      scaled_df['Curso Founder'].value_counts()

    scaled_df['Nome da empresa'] = scaled_df['Nome da empresa'].apply(lambda x: str(round(x, 5)))
    print('[INFO] Nomes da empresa convertidos para string')
    
    print('[INFO] Início da análise dos dados sintetizados')
    historico = scaled_df

    print('[INFO] Filtro dos dados sintetizados')
    print('[INFO] Removendo empresa cujo numero de clientes eh menos que a quantidade de funcionarios')

    historico.drop(historico.loc[historico['Número de Clientes'] < historico['Quantidade de funcionários']].index, inplace=True)

    print('[INFO] Removendo empresa cujas datas nao condizem: fundacao < submissao < decisao')
    for i in ("Data da submissão", "Data de fundação", "Data Decisão"):
      historico[i] = pd.to_datetime(historico[i])

    # Combinações incoerentes:
    historico.drop(historico.loc[historico['Data de fundação'] >= historico['Data da submissão']].index, inplace=True)
    historico.drop(historico.loc[historico['Data de fundação'] >= historico['Data Decisão']].index, inplace=True)
    historico.drop(historico.loc[historico['Data da submissão'] >= historico['Data Decisão']].index, inplace=True)

    # Devolvendo as datas para o formato de interpretação
    for i in ("Data da submissão", "Data de fundação", "Data Decisão"):
      # Retornando à formatação de datas do padrão brasileiro entendido como input do usuário (DD-MM-YYYY)
      historico[i] = historico[i].apply(lambda x: str(x.day) + "/" + str(x.month) + "/" + str(x.year))

    print('[INFO] Início da analise da variavel da decisao de investimento')
    # Reinicializando a variável-alvo:
    historico['Investiu?'] = "analisar"

    # Interpretação das datas das amostras
    for i in ("Data da submissão", "Data de fundação", "Data Decisão"):
      historico[i] = pd.to_datetime(historico[i])

    print('[INFO] Regras de investimento para reduzir analise manual')
    print('* Nao investe em empresas que submetem no mesmo ano de fundacao da empresa,')
    print('ou se a decisao foi tomada em menos de um mes apos submissao')
    # Empresas recém-criadas
    historico['Investiu?'] = historico.apply(lambda row: "Não" if (row['Data de fundação'].year == row['Data da submissão'].year) else row['Investiu?'], axis = 1)
    # Decisões que vieram rapidamente, entende-se que foram cortadas rápidamente
    historico['Investiu?'] = historico.apply(lambda row: "Não" if (row['Data Decisão'].month - row['Data da submissão'].month <= 1) else row['Investiu?'], axis = 1)

    # Devolvendo as datas para o formato de interpretação
    for i in ("Data da submissão", "Data de fundação", "Data Decisão"):
      # Retornando à formatação de datas do padrão brasileiro entendido como input do usuário (DD-MM-YYYY)
      historico[i] = historico[i].apply(lambda x: str(x.day) + "/" + str(x.month) + "/" + str(x.year))
      
    print('* Muitos funcionários (acima do 2º quartil) e sem gerar receita')  
    # Muitos funcionários (acima do 2º quartil) e sem gerar receita
    historico['Investiu?'] = historico.apply(lambda row: "Não" if (row['Quantidade de funcionários'] > historico['Quantidade de funcionários'].quantile(0.5)
                                                                  and row['Gerando receita?'] == 'Não') else row['Investiu?'], axis = 1)

    print('* CAC alto (acima do 2º quartil) e sem gerar receita') 
    # CAC alto (acima do 2º quartil) e sem gerar receita
    historico['Investiu?'] = historico.apply(lambda row: "Não" if (row['CAC histórico (R$)'] > historico['CAC histórico (R$)'].quantile(0.5)
                                                                  and row['Gerando receita?'] == 'Não') else row['Investiu?'], axis = 1)

    print('* Poucos clientes (abaixo do 2º quartil), clientes não recorrentes e CAC alto (acima do 2º quartil)') 
    # Poucos clientes (abaixo do 2º quartil), CAC alto (acima do 2º quartil) e não recorrentes
    historico['Investiu?'] = historico.apply(lambda row: "Não" if (row['CAC histórico (R$)'] > historico['CAC histórico (R$)'].quantile(0.5)
                                                                  and row['Número de Clientes'] < historico['Número de Clientes'].quantile(0.5)
                                                                  and row['Clientes Recorrentes?'] == 'Não') else row['Investiu?'], axis = 1)

    print('* Empresas tech, sem produto próprio e founder não técnico') 
    # Empresas tech, sem produto próprio e founder não técnico
    historico['Investiu?'] = historico.apply(lambda row: "Não" if (row['Indústria'] == "Tech"
                                                                  and (row['Curso Founder'] != 'Ciência da Computação' or row['Curso Founder'] != 'Engenharia')
                                                                  and row['Produto próprio?'] == 'Não') else row['Investiu?'], axis = 1)
                    
    print('[INFO] Fim da analise da variavel da decisao de investimento')

    print('[INFO] Carregando decisao de investimento completa: automatizada + manual')
    if(IS_MANUAL_ANALYSIS_DONE):
      # Caso exemplo: análise manual fora feita previamente
      analises = pd.read_csv(base_analisadas_manual)

      historico = historico.merge(analises, how='left', left_index=True, right_on='Unnamed: 0')
      historico.drop(['Investiu?_x', 'Unnamed: 0'], axis=1, inplace=True)
      historico.rename(columns={'Investiu?_y': 'Investiu?'}, inplace=True)

    else:
      # Rotina de análise manual das empresas que faltam
      from IPython.display import clear_output 
      # Percorrendo todas as amostras:
      for amostra in range(historico.shape[0]):
        # a variável-alvo está na posição 13 do DataFrame
        if (historico.iloc[amostra, 13] == 'analisar'):
          print(historico.iloc[amostra])
          historico.iloc[amostra, 13] = input('Decisão: ')
          print("=======================================================")
          clear_output()

    print('[INFO] Salvando base crua de dados historicos')

    json_to_save = {
      '_user_name': current_user,
      '_theory_name': theory_name
    }
    json_to_save['historic_data'] = historico.to_dict(orient="index")

    json_to_update = { "$set": json_to_save }
    mongo_response = requests.put(GLOBAL_URL + 'investors_theory/historic_data/{}/{}'.format(current_user,theory_name),
                                  json = json_to_update)

    if mongo_response.status_code == 400:
      mongo_response = requests.post(GLOBAL_URL + 'investors_theory/historic_data', json = json_to_save)

    if mongo_response.status_code == 200:
      print('[SUCCESS] Fase 1 - Salvou dados no mongo')

    end = time.time()
    print('[SUCCESS] Fim da etapa 01. Durou: {} segundos'.format(round(end-start, 3)))

    return historico, round(end-start, 3)

if __name__ == "__main__":
    main()