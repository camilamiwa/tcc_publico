import time
start = time.time()
import pandas as pd
import numpy as np
import requests

"""## 3. Preparação e limpeza dos dados

Quanto à limpeza dos dados, num problema de Data Science o ideal seria analisar o dataset fornecido e ser uma abordagem bem personalizada e específica (apesar de metódica).

Para o escopo deste trabalho, bastará apenas lidar com problemas "comuns" e previamente antecipados:

- Dados faltantes ou nulos
- Nomes das variáveis
- Transformação em Booleanos

Em um eventual produto final, a jornada dos usuários pode ser pensada para facilitar essa padronização e garantir que os tratamentos nesta etapa sejam esses mesmo.
"""

def ticket_medio(receita, num_clientes):
        if num_clientes ==  0:
            return 0
        else:
            return receita/num_clientes

def main(start_file_name = r'bases_csv\01_historico_base_crua.csv',
          final_file_name = r'bases_csv\02_historico_tratado.csv',
          GLOBAL_URL = 'http://127.0.0.1:5000/', 
          current_user = 'jocaJ', theory_name = 'jocaJ'):

    print('[INFO] Inicio da etapa 02 - Tratamento de dados')

    # historico = pd.read_csv(start_file_name)

    get_from_mongo = requests.get(GLOBAL_URL + 'investors_theory/historic_data/{}/{}'.format('dtypes', 'dtypes'))
    columns_dtypes = get_from_mongo.json()['dtypes']
    for key, value in columns_dtypes.items():
        columns_dtypes[key] = np.dtype(value)

    get_from_mongo = requests.get(GLOBAL_URL + 'investors_theory/historic_data/{}/{}'.format(current_user,theory_name))

    historico = pd.DataFrame.from_dict(get_from_mongo.json()['historic_data'], orient = 'index').astype(dtype = columns_dtypes)
    historico.reset_index(inplace=True, drop = True)

    print('[INFO] Formatando nomes de colunas e dados do tipo datetime e boleano')

    #Substituição dos nomes das variáveis por nomes SEM espaço nem caracteres especiais, para poder seguir com os métodos Panda
    historico.rename(
        columns={'Nome da empresa':'Nome_empresa',          # passando o nome antigo e novo como um dicionário
                'Data da submissão':'Data_submissao',
                'Data de fundação': 'Data_fundacao',
                'Quantidade de funcionários':'Quantidade_funcionarios',
                'Indústria': 'Industria',
                'Produto próprio?': 'Produto_proprio',
                'Gerando receita?': 'Gerando_receita',
                'Receita mensal (R$/mês)':'Receita_mensal',
                'Número de Clientes':'Numero_clientes',
                'Clientes Recorrentes?':'Clientes_recorrentes',
                'CAC histórico (R$)':'CAC_historico',
                'Curso Founder':'Curso_Founder',
                'Data Decisão':'Data_decisao',
                'Investiu?': 'Investiu'
                },
        inplace = True              # para alterar o objeto Panda _tese_, e não criar uma cópia
    )

    # Método de transformação dos dados para numérico: pd.to_numeric(df[_variável_], errors='coerce')
    ## Coerce define como NaN qualquer erro

    # Conversão das datas (atualmente tipo Object) em DateTime: pd.to_datetime(df._variável_)
    historico.Data_submissao = pd.to_datetime(historico.Data_submissao)
    historico.Data_fundacao  = pd.to_datetime(historico.Data_fundacao)
    historico.Data_decisao   = pd.to_datetime(historico.Data_decisao)

    # Transformando as variáveis de pergunta em 1 ou 0 (bool)

    historico['Produto_proprio'] = historico['Produto_proprio'].map({'Sim': True, 'Não': False})      # Substitui a string por um booleano
    historico['Gerando_receita'] = historico['Gerando_receita'].map({'Sim': True, 'Não': False})
    historico['Clientes_recorrentes'] = historico['Clientes_recorrentes'].map({'Sim': True, 'Não': False})
    historico['Investiu'] = historico['Investiu'].map({'Sim': True, 'Não': False})

    """------------------------
    Apesar da preparação dos dados, observa-se que as variáveis `{Industria, Curso_Founder}` 
    são variáveis **categóricas**. Isto é, são valores de um conjunto não-numérico e finito, 
    geralmente (como neste caso) representados por textos.

    Desse modo, é necessário convertê-las para valores numéricos e assim conseguir seguir na aplicação do modelo.
    Para isso, será aplicado o método **One-Hot Encoding** - "criar uma variável numérica para cada categoria,
    com os valores `0` ou `1` representando a presença dessa categoria para cada registro".

    A seguir um exemplo aplicado na coluna `Industria` de nosso DataSet.
    """

    print('[INFO] One-hot coding para colunas Industria e Curso_Founder')
    # O One-Hot Encoding pode ser aplicado pela função 'get_dummies' que criará novas variáveis
    # pd.get_dummies(historico.Industria).head()

    # O passo seguinte será concatenar essas novas variáveis ao nosso dataset base, e apagar a coluna anterior (Indústria)
    historico = pd.concat([historico.drop("Industria", axis=1), pd.get_dummies(historico.Industria, prefix='Industria')], axis=1) # nos métodos 'drop' e 'concat', o atributo 'axis = 1' indica que a operação é entre colunas
    
    # O mesmo para a variável Curso_founder agora
    historico = pd.concat([historico.drop("Curso_Founder", axis=1), pd.get_dummies(historico.Curso_Founder, prefix='Course')], axis=1)

    """Nota-se ainda assim que a variável `Nome_empresas` analisadas ainda é do tipo `object`.
    Como mencionado anteriormente, a retiraremos da base para o modelo tanto por uma questão de LGPD 
    e prezar pela anonimimidade dos dados quanto por eficiência do algoritmo."""

    historico.drop("Nome_empresa", axis=1, inplace = True)

    """## 4. Análise exploratória dos dados recebidos (EDA)

    Uma etapa importante dos projetos de análise de dados e um dos principais valores deste projeto
    é entender as particularidades e relações dos dados fornecidos. Evidentemente, é um processo bastante
    específico e geralmente feito caso a caso.

    Para este projeto, aplicaremos os métodos mais comuns de análise do conjunto e tentaremos identificar
    algumas relações que são frequentemente úteis.
    """

    # pdb.set_trace()
    # # Como as variáveis estão correlacionadas entre si? Há o método corr que permite acessarmos isso: 
    # historico.corr()

    # #Como as variáveis estão correlacionadas com a nossa variável alvo - INVESTIU?
    # historico.corr()['Investiu']
    # pdb.set_trace()

    # # Também, ao invés de printar no console, pode-se montar um gráfico para analisarmos essas relações de uma maneira mais visual:

    # plt.figure(figsize=(10,10))
    # sns.heatmap(historico.corr(),annot=True, fmt=".2f", linewidth=.5)

    # plt.show()

    """## 5. Engenharia de variáveis

    ### 5.1 Novas variáveis

    Nesta etapa, podemos adicionar variáveis mais explicativas para o modelo. Como por exemplo, o `ticket_medio`.
    """

    print('[INFO] Adicionando variáveis derivadas das colunas existentes')

    historico['Ticket_medio'] = historico.apply(lambda row: ticket_medio(row['Receita_mensal'], row['Numero_clientes']), axis=1)

    """Ainda também, é interessante destacar que os modelos usados aqui, não conseguem interpretar datas
    tão precisamente (afinal, este tipo de problemas não está classificado como de Séries Temporais
    - que envolvem outros algoritmos). Então, podemos agir sobre as variáveis: `Data_submissao`, `Data_fundacao` e `Data_decisao`:"""

    # A data da decisão sobre investimento não é importante para a nossa análise
    historico.drop("Data_decisao", axis=1, inplace = True)

    # Agora, das outras duas datas, podemos extrair o tempo de operação da empresa e adicionar essa variável ao modelo!
    historico['Tempo_mercado_meses'] = historico['Data_submissao'] - historico['Data_fundacao']
    historico['Tempo_mercado_meses'] = (historico['Tempo_mercado_meses'] / np.timedelta64(1,'M')).astype(float)

    historico.drop(["Data_fundacao", "Data_submissao"], axis=1, inplace = True)

    # historico.to_csv(final_file_name, index = False)

    json_to_save = {
      '_user_name': current_user,
      '_theory_name': theory_name
    }
    json_to_save['historic_tratado'] = historico.to_dict(orient="index")

    json_to_update = { "$set": json_to_save }
    mongo_response = requests.put(GLOBAL_URL + 'investors_theory/historic_tratado/{}/{}'.format(current_user,theory_name),
        json = json_to_update)

    if mongo_response.status_code == 400:
      mongo_response = requests.post(GLOBAL_URL + 'investors_theory/historic_tratado', json = json_to_save)

    if mongo_response.status_code == 200:
      print('[SUCCESS] Fase 2 - Salvou dados no mongo')

    end = time.time()
    print('[SUCCESS] Fim da etapa 02. Durou: {} segundos'.format(round(end-start, 3)))

    return historico, round(end-start, 3)

if __name__ == "__main__":
    main()