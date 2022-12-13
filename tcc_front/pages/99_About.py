import streamlit as st

st.title("Sobre o projeto")
st.subheader("Trabalho de conclusão de curso: Escola Politécnica da USP - 2022")

col1, col2 = st.columns(2)

with col1:
    st.write("Alunos do projeto:\n  - Aline Lorena Tsuruda\n  - Camila Miwa Ivano\n  - Vinícius Cardieri Lopez")

with col2:
    st.write("Orientados por:\n  - Prof. Dr. Reginaldo Arakaki\n  - Co-Orientador: Victor Takashi Hayashi")

st.markdown("""---""")
st.subheader("Objetivo")

st.write("Este projeto tem o intuito de aplicar os conceitos estudados ao longo do curso de Engenharia Elétrica, ênfase em Computação para a criação de uma ferramenta de suporte à decisão de investimentos.")

st.write("A ferramenta, recebe dos investidores uma tese de investimentos implícita através de um histórico de empresas que já foram previamente analisadas. A partir desses exemplos, faz um tratamento de dados prévio (incluindo rotinas de Data Augmentation e Engenharia de Variáveis) e treina dois algoritmos de Machine Learning Supervisionados para classificação: K-Nearest Neighbours e Random Forest.")
st.write("Em seguida, recebe a descrição de uma empresa candidata para avaliar se a mesma está aderente às teses cadastradas na plataforma.")

st.markdown("""---""")
st.subheader("Trabalho completo")
st.write("Para conhecer mais do projeto, acesse a nossa [Landing Page](https://sites.google.com/usp.br/tcc-analise-empresas-poli22/in%C3%ADcio)!")

st.markdown("""---""")
st.subheader("Contatos")
st.write("  - Aline Lorena Tsuruda: [LinkedIn](https://www.linkedin.com/in/aline-tsuruda/)\n  - Camila Miwa Ivano: [LinkedIn](https://www.linkedin.com/in/camila-miwa-ivano/)\n  - Vinícius Cardieri Lopez: [LinkedIn](https://www.linkedin.com/in/vinicius-cardieri-lopez-79ba17163/)")
