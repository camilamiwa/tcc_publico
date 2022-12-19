import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page
import datetime
import time

from PIL import Image

import requests

import investor_json_examples

import a01_sintese_preparacao_dados
import a02_tratamento_dados
import a03_filtro_parametros
import a04_estatisticas_modelo
import a05_analise_nova_empresa

from sklearn.metrics import (confusion_matrix, ConfusionMatrixDisplay, classification_report)

global_url = 'http://127.0.0.1:5000/'
isApiRunning = True
#isApiRunning = False

###########################
# FrontEnd pelo StreamLit #
###########################

st.title("TCC - AUTOMATIZAÇÃO DE ANÁLISE DE EMPRESAS PARA AUXÍLIO DE DECISÃO DE INVESTIMENTOS")
st.write("Ferramenta de suporte para decisão de investimento em startups a partir de Machine Learning")

st.subheader("Bem-vindo ao projeto, primeiramente, nos diga quem é você e faça seu cadastro:")
perfil = st.radio('Eu sou:', ['Investidor', 'Empreendedor'])
st.markdown("""---""")
isInvestor = False

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index = False).encode('utf-8')

if perfil == 'Investidor':

  #Inicializando as variáveis da sessão
  if 'investor_username' not in st.session_state:
    st.session_state['investor_username'] = ''
  if 'theory_name' not in st.session_state:  
    st.session_state['theory_name'] = ''
  if 'global_url' not in st.session_state:
    st.session_state['global_url'] = 'http://127.0.0.1:5000/'

  isInvestor = True
  avaliar_empresa = False

  st.write("Legal! Agora, faremos seu cadastro. Para isso, precisaremos de um registro em planilha de empresas que você já analisou anteriormente e decidiu (investir ou não). Baixe a seguir os nossos templates!\n")
  
  col1, col2 = st.columns(2)
  
  # Modelo para baixar e preencher
  with col1:
    st.write("Baixe o modelo de importação dos dados! Preencha-o com as informações de todas as empresas que você já avaliou, e a decisão final!")
   
    if isApiRunning:
      pandas_load = pd.read_json("investor_empty.json")
      guia_importacao = pandas_load.to_csv(index = False)

      baixou_modelo = st.download_button('Download template',
                                        data=guia_importacao,
                                        file_name='guia_importacao_tese.csv',
                                        mime='text/csv')
    else: 
      guia_importacao =  '''teste, oi'''
      baixou_modelo = st.download_button('Download modelo', guia_importacao, 'guia_importacao_tese.csv')    

    if (baixou_modelo):
      st.write('Download feito! Não se esqueça de respeitar a formatação do arquivo!')
  
  # Testes usados
  with col2:
    st.write("Caso queira entender como o sistema funciona primeiro, preparamos este conjunto de dados para você simular!")
    if isApiRunning:
      pandas_load = pd.read_csv("Tese_Investimento_Exemplo.csv")
      st.write(pandas_load.head())
      exemplo_tese = pandas_load.to_csv(index = False)

      baixou_modelo = st.download_button('Download modelo',
                                        data=exemplo_tese,
                                        file_name='exemplo_tese.csv',
                                        mime='text/csv')
    else: 
      exemplo_tese =  '''teste, oi'''
      baixou_modelo = st.download_button('Download exemplo', exemplo_tese, 'exemplo_tese.csv')
    if (baixou_modelo):
      st.write('Download feito! Siga adiante!')
  st.markdown("""---""")

  st.header("Faça seu cadastro como investidor e comece a analisar empresas candidatas!")  
  # Cadastro inicial com informações pessoais e da tese de investimentos
  with st.form("Nos conte mais sobre você:", clear_on_submit=False):

    nome = st.text_input("Nome:", value="Fulano da Silva")
    email = st.text_input("Email:", value="fulano", placeholder="fulano.silva@gmail.com")
    telefone = st.text_input("Telefone:", value=11987654321, placeholder="(__) _____-____")
    senha = st.text_input("Senha:", placeholder="****", value='adm123', type="password")
    
    st.write("\nAgora, sobre sua tese de investimentos:")

    tese = st.file_uploader('Faça upload das últimas empresas que você analisou aqui: (CSV)', type='csv')
    nome_tese = st.text_input("Identificador (nome) da sua tese:", value='Standard', placeholder="Tese do Fulano")

    aceito_lgpd = st.checkbox('Concordo em compartilhar essas informações e sei que o projeto armazenará os dados de minha tese anonimizados, não sendo permitido o compartilhamento dos mesmos.')
    submit = st.form_submit_button("Começar análise")

  if (submit and aceito_lgpd and tese is not None):
    
    add_profile = {
      "_user_name": email,
      "name" : nome,
      "email" : email,
      "phone" : telefone,
      "investor": isInvestor,
      "password": senha,
      "theory_name": nome_tese
    } 

    inserted = requests.post(global_url + 'profile', json = add_profile)

    st.success(f"{nome}, cadastro concluído com sucesso!")
    tese = pd.read_csv(tese)

    # Iniciar EDA e descrição da tese
    st.markdown("""---""")
    st.subheader('Análise da tese "' + nome_tese + '":')
    with st.spinner('Analisando sua tese...'):
      # Rotinas: Data Augmentation; EDA
      historico_cru, duracao_a01 = a01_sintese_preparacao_dados.main(tese_exemplo=tese, current_user=email, theory_name=nome_tese)
      # Rotinas: Limpeza dos dados; Engenharia de variáveis
      historico_tratado, duracao_a02 = a02_tratamento_dados.main(current_user=email, theory_name=nome_tese)

      st.write("Terminamos o tratamento! Este é o cabeçalho (cinco primeiras linhas) de seu histórico de decisões que está sendo analisado:")
      st.write(historico_cru.drop('Nome da empresa', axis=1).head())

    with st.spinner('Agora, estamos selecionando as colunas que têm mais influência na sua decisão!'):
      # Rotinas: Seleção de variáveis
      historico_filtrado, var_explicativas, duracao_a03 = a03_filtro_parametros.main(current_user=email, theory_name=nome_tese)
      st.write("Estas são as variáveis que identificamos maior correlação com a sua decisão de investir ou não:\n")
      st.write(var_explicativas.drop('Investiu', axis=1).columns.to_list())

    with st.spinner('Avaliando os modelos disponíveis para sua tese...'):
      # Rotinas: Treino dos modelos; aplicação dos dois
      labels_rf, labels_knn, score_rf, score_knn, y_val, y_pred_rf, y_pred_knn, duracao_a04 = a04_estatisticas_modelo.main(investor_name=email, theory_name=nome_tese)

      if (score_rf > score_knn):
        st.write("O modelo escolhido foi o Random Forest!")
        st.write("Acurácia no conjunto de validação: {:.3f}".format(score_rf))
        
        cm = confusion_matrix(y_val, y_pred_rf, labels=labels_rf)
        cm = pd.DataFrame(cm, index=["Previu - Não investir", "Previu - Investir"], columns=["Verdade - Não investir", "Verdade - Investir"])
        st.write("Matriz de confusão:\n", cm)

        cr = classification_report(y_val, y_pred_rf, output_dict=True)
        cr = pd.DataFrame(cr)
        cr = cr.applymap(lambda x: str(int(x)) if abs(x - int(x)) < 1e-6 else str(round(x,2)))
        st.write("Relatório do modelo:\n", cr.T)

      else:
        st.write("O modelo escolhido foi o K-Nearest Neighbours")
        st.write("Acurácia no conjunto de validação: {:.3f}".format(score_knn))
        
        cm = confusion_matrix(y_val, y_pred_knn, labels=labels_knn)
        cm = pd.DataFrame(cm, index=["Previu - Não investir", "Previu - Investir"], columns=["Verdade - Não investir", "Verdade - Investir"])
        st.write("Matriz de confusão:\n", cm)

        cr = classification_report(y_val, y_pred_knn, output_dict=True)
        cr = pd.DataFrame(cr)
        cr = cr.applymap(lambda x: str(int(x)) if abs(x - int(x)) < 1e-6 else str(round(x,2)))
        st.write("Relatório do modelo:\n", cr.T)

  avaliar_empresa = st.button("Finalizar cadastro e avaliar uma empresa!")
    
  if(avaliar_empresa):
    st.session_state.investor_username = email
    st.session_state.theory_name = nome_tese
    switch_page("Sou_Investidor")

elif perfil == 'Empreendedor':

  #Inicializando as variáveis da sessão
  if 'founder_name' not in st.session_state:
    st.session_state['founder_name'] = ''
  if 'theory_name' not in st.session_state:
    st.session_state['theory_name']  = ''
  if 'global_url' not in st.session_state:
    st.session_state['global_url'] = 'http://127.0.0.1:5000/'

  dt_fund = datetime.datetime.now() + datetime.timedelta(days=-320)

  st.header("Nos conte mais de sua empresa!")
  # Cadastro inicial com informações pessoais e da tese de investimentos
  with st.form("Primeiro, faremos seu cadastro para depois você procurar seus investidores mais estratégicos!", clear_on_submit=False):
    nome_founder =  st.text_input("Nome founder:", placeholder="Fulano da Silva", value='Ciclano Junior')
    email_founder = st.text_input("Email founder:", placeholder="fulano.silva@gmail.com", value='ciclano')
    telefone_founder = st.text_input("Telefone founder:", placeholder="(__) _____-____", value='11956784321')
    nome_empresa =  st.text_input("Nome da empresa candidata:", placeholder="Nubank", value='Company Ldta.')
    data_fundacao = st.date_input("Data da fundação:", max_value=datetime.date.today(), value=dt_fund)
    data_submissao = datetime.date.today()
    qtd_funcionarios = st.number_input("Quantidade de funcionários:", min_value=1, value=40, step=1, format='%d')
    industria = st.text_input("À qual categoria sua indústria pertence?", placeholder="Fintech", value="Fintech")
    prod_proprio = st.radio('Seu produto principal é próprio?', ['Sim', 'Não'])
    cnpj_empresa = st.number_input("CNPJ da empresa candidata: ", min_value=1, value=12345678000190, step=1, help='Digite apenas os números!', format='%d')
    ger_receita = st.radio('Já está gerando receita?', ['Sim', 'Não'])
    if (ger_receita == 'Sim'):
        receita = st.number_input("Receita mensal (R$):", min_value=0, value=7400, step=1, format='%d')
    else: receita = 0
    num_clientes = st.number_input("Número de clientes:", min_value=1, value=100, step=1, format='%d')
    cli_recor = st.radio('Clientes são recorrentes?', ['Sim', 'Não'])
    cac_hist = st.number_input("CAC histórico (R$/clientes):", min_value=1, value=240, step=1, format='%d')
    curso_founder = st.text_input("Curso do founder:", placeholder="Engenharia", value="Engenharia")

    submit = st.form_submit_button("Fazer cadastro")                                 
    if submit:
        add_profile = {
          "_user_name": email_founder,
          "name" : nome_founder,
          "email" : email_founder,
          "phone" : telefone_founder,
          "investor": False,
          #"password": senha_founder
        } 

        profile_inserted = requests.post(global_url + 'profile', json = add_profile)
        
        if profile_inserted:
          add_company = {
            "_company_cnpj": cnpj_empresa,
            "_company_id": cnpj_empresa,
            "_user_name" : email_founder,
            "oficial_name" : str(nome_empresa),
            "data_fundacao" : str(data_fundacao),
            "data_submissao" : str(data_submissao),
            "qtd_funcionarios" : qtd_funcionarios,
            "industria" : industria,
            "prod_proprio" : True if (prod_proprio == 'Sim') else False,
            "gera_receita": True if (ger_receita == 'Sim') else False,
            "receita": receita,
            "num_clientes": num_clientes,
            "cli_recor": True if (cli_recor == 'Sim') else False,
            "cac_hist": cac_hist,
            "curso_founder": curso_founder            
          }

          company_inserted = requests.post(global_url + 'company', json = add_company)
          if (company_inserted.status_code == 400):
            json_to_update = { "$set": add_company}
            company_inserted = requests.put(global_url + 'company/id/' + str(cnpj_empresa), json = json_to_update)

        st.success(f'''{nome_founder}, seu cadastro e da empresa {nome_empresa} foram concluídos com sucesso!
                    Redirecionando para a página de escolha de teses em instantes...''')
        st.session_state.founder_name = nome_founder
        st.session_state.theory_name  = cnpj_empresa

        time.sleep(5)
        switch_page("Sou_Founder")

# Explicação do projeto
st.markdown("""---""")
st.subheader("Propósito do projeto:")
st.write("Temos a visão de nos tornarmos um canal de conexão entre Investidores e Empreendedores. Através desta plataforma, é possível encontrar potenciais novas parcerias!")
about = st.button("Conhecer saber mais do projeto!")
if(about):
    switch_page("About")