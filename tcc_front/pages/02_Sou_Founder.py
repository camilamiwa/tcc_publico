import streamlit as st
import pandas as pd
import datetime
import time
from pymongo import MongoClient
import a05_analise_nova_empresa

nome_founder = st.session_state.founder_name
cnpj_empresa = st.session_state.theory_name
global_url = st.session_state.global_url

def get_database(database_name):
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://tcc_avc:adm321@tcccluster.wzgcevd.mongodb.net/test"
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    db_client = MongoClient(CONNECTION_STRING)
    # Create the database for our example (we will use the same database throughout the tutorial
    return db_client[database_name]

st.title("Olá " + nome_founder + ", vamos simular sua empresa em uma das nossas teses")

# Camila - GET parâmetros de análise deste empreendedor
# criar dataset X_empreendedor a partir disso

# Pegando os investidores cadastrados na plataforma
investors_db  = get_database('users')
investors_col = investors_db['profile']
cursor = investors_col.find({"theory_name":{"$exists":True}})

nome_investidores_cadastrados = []
email_investidores_cadastrados = []
theory_name_investidores_cadastrados = []

for i in cursor:
  nome_investidores_cadastrados.append(i['name'])
  email_investidores_cadastrados.append(i['email'])
  theory_name_investidores_cadastrados.append(i['theory_name'])

investidores_cadastrados = pd.DataFrame(list(zip(nome_investidores_cadastrados,
                                                 email_investidores_cadastrados,
                                                 theory_name_investidores_cadastrados)),
                                        columns =['name', 'email', 'theory_name'])
# Ou podemos fechar para deixar Hard-Coded alguns só hehe
# nome_investidores_cadastrados = ["Anima", "Sequoia Capital", "Warren Buffet"]

investidor = st.selectbox('Escolha o investidor que deseja consultar:', nome_investidores_cadastrados)

email_investor = investidores_cadastrados.loc[(investidores_cadastrados['name']) == investidor,'email'].values[0]
nome_tese = investidores_cadastrados.loc[(investidores_cadastrados['name']) == investidor,'theory_name'].values[0]

st.markdown("""---""")

st.subheader("Dados do investidor:")
st.write("Nome do investidor: " + str(investidor))
st.write("Email do investidor: " + email_investor)
st.write("Nome da tese: " + nome_tese)

st.markdown("""---""")

st.subheader("Análise:")
inicio_analise = st.button("Começar a análise da empresa de acordo com a tese " + nome_tese)
if(inicio_analise):
  a05_analise_nova_empresa.main(global_url, email_investor, nome_tese, cnpj_empresa)