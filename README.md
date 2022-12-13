
# AUTOMATIZAÇÃO DE ANÁLISE DE EMPRESAS PARA AUXÍLIO DE DECISÃO DE INVESTIMENTOS

Este projeto tem o intuito de aplicar os conceitos estudados ao longo do curso de Engenharia Elétrica, ênfase em Computação, para a criação de uma ferramenta de suporte à decisão de investimentos. 

O projeto é dividido em três partes:
- Front (telas)
- Back (serviço API)
- Algoritmo (IA)

Para rodar o projeto completo, é necessário rodar as três partes.


## Instalando

Clone o repositório

```bash
    git clone https://github.com/camilamiwa/tcc_publico.git
```

### Configurando

Para configurar o ambiente e rodar o projeto corretamente, instale as bibliotecas necessárias.

Antes de instalar as bibliotecas, crie um ambiente virtual e depois de ativá-lo, instale as bibliotecas.

Todas as bibliotecas necessárias estão listadas no arquivo ```requirements.txt```.

Como esse projeto está dividido em 3 partes, é necessário rodar as instruções 3 vezes.

A configuração completa é apresentada:

```bash
    cd tcc_algoritmo_ia
    python3 -m venv venv_algoritmo
    venv_algoritmo\Scripts\activate
    pip install -r requirements.txt
    deactivate

    cd tcc_front
    python3 -m venv venv_front
    venv_front\Scripts\activate
    pip install -r requirements.txt
    deactivate

    cd tcc_service
    python3 -m venv venv_back
    venv_back\Scripts\activate
    pip install -r requirements.txt
    deactivate
```

## Conexão com o banco de dados

Entre em contato para pedir a string de conexão com o nosso banco.

Insira a string de conexão no arquivo ```connection_string.py```.

## Rodando localmente

Para rodar localmente, é necessário rodar o serviço API em um shell, e em outro shell rodar as telas UI.

Para rodar o serviço API (primeiro shell):
```bash
    cd tcc_service
    venv_back\Scripts\activate
    python pymongo_test.py
```

Este shell deve ficar aberto e com o serviço rodando, este serviço API fornece os endpoints necessários.

Em um segundo shell, rodar as telas:
```bash
    cd tcc_front
    venv_front\Scripts\activate
    streamlit run 00_Cadastro.py
```

Este segundo shell fornecerá um endereço local, abrir o link com um navegador mostra as telas desenvolvidas.

Este shell já tem o componente do algoritmo IA embutido.

## Algoritmo IA

### Teste do algoritmo isolado

Para testar o núcleo do projeto (algoritmo IA) por completo:
```bash
    cd tcc_algoritmo_ia
    venv_algoritmo\Scripts\activate
```

Crie pastas para armazenar os resultados intermediários:
```bash
    mkdir bases_csv
    mkdir novas_empresas_csv
```

Para rodar partes específicas:
```bash
    python <nome_arquivo>.py
```

Por exemplo:
```bash
    python a00_main.py
```

A base histórica deve ser inserida na pasta ```bases_para_analise```.
E os dados da empresa a ser analisada devem ser colocados na pasta ```novas_empresas_csv```.

## Feedbacks

Desenvolvemos esse projeto como nosso projeto de conclusão de curso, ficaremos contentes em saber como podemos aprimorar. Entre em contato conosco!

