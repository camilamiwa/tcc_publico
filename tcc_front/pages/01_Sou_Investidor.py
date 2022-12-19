import streamlit as st
import pandas as pd
import datetime
import time
import requests

import a05_analise_nova_empresa

email_investor = st.session_state.investor_username
nome_tese = st.session_state.theory_name
global_url = st.session_state.global_url
dt_fund = datetime.datetime.now() + datetime.timedelta(days=-320)

st.title('Tese "' + nome_tese + '" carregada com sucesso')
st.write("Preencha os dados a seguir para avaliar a aderência da empresa à tese:")

with st.form("Preencha os dados a seguir para avaliar a aderência da empresa à tese:", clear_on_submit=False):
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

        # profile_inserted = requests.post(global_url + 'profile', json = add_profile)
        
        # if profile_inserted:
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
          #novas coisas que adicionei:
          "gera_receita": True if (ger_receita == 'Sim') else False,
          "receita": receita,
          "num_clientes": num_clientes,
          "cli_recor": True if (cli_recor == 'Sim') else False,
          "cac_hist": cac_hist,
          "curso_founder": curso_founder            
        }

          # company_inserted = requests.post(global_url + 'company', json = add_company)
          # if (company_inserted.status_code == 400):
          #   json_to_update = { "$set": add_company}
          #   company_inserted = requests.put(global_url + 'company/id/' + str(cnpj_empresa), json = json_to_update)

        st.success('Empresa submetida para análise!')
        a05_analise_nova_empresa.main(global_url, email_investor, nome_tese, cnpj_empresa)