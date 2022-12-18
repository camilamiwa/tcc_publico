import json
from pymongo import MongoClient
from flask import Flask, request
import bson.json_util as json_util
from connection_string import conn_string

app = Flask(__name__)
app.config["DEBUG"] = True

isTesting = True

# Esta função retorna uma conexão com o database pedido
def get_database(database_name):
    # Definição da string de conexão 
    CONNECTION_STRING = conn_string
    # Conexão com o Mongo via string de conexão
    db_client = MongoClient(CONNECTION_STRING)
    # Criação do database pedido
    return db_client[database_name]

# Início da definição dos endpoints

# Um pedido feito para http://localhost:5000/<endpoint>

# Formato padrão para definição dos endpoints
# @app.route('/<endpoint>', methods=[<seleção de alguma operação CRUD>])
# Na sequência define-se a lógica implementada pelo endpoint
# As operações para cada database são análogas, por isso elas serão mais
#  detalhadas para os usuários, e as observações serão parecidas

# Endpoints relacionados ao usuário

@app.route('/delete_all/profile', methods=['DELETE'])
def delete_all_user_profile():
    profile_collection = db_users['profile']
    profile_collection.delete_many({})

@app.route('/delete_all/results', methods=['DELETE'])
def delete_all_results():
    results_collection = db_results['results_and_comments']
    results_collection.delete_many({})

@app.route('/delete_all/investors/data', methods=['DELETE'])
def delete_all_investors_data():
    investors_collection = db_investors['historic_data']
    investors_collection.delete_many({})

@app.route('/delete_all/investors/filtrado', methods=['DELETE'])
def delete_all_investors_filtrado():
    investors_collection = db_investors['historic_filtrado']
    investors_collection.delete_many({})

@app.route('/delete_all/investors/tratado', methods=['DELETE'])
def delete_all_investors_tratado():
    investors_collection = db_investors['historic_tratado']
    investors_collection.delete_many({})

@app.route('/delete_all/companies', methods=['DELETE'])
def delete_all_companies():
    company_collection = db_companies['raw_data']
    company_collection.delete_many({})

@app.route('/delete_all/cluster', methods=['DELETE'])
def delete_entire_mongo():
    profile_collection = db_users['profile']
    profile_collection.delete_many({})

    results_collection = db_results['results_and_comments']
    results_collection.delete_many({})

    investors_collection = db_investors['historic_data']
    investors_collection.delete_many({})

    investors_collection = db_investors['historic_filtrado']
    investors_collection.delete_many({})

    investors_collection = db_investors['historic_tratado']
    investors_collection.delete_many({})

    company_collection = db_companies['raw_data']
    company_collection.delete_many({})
    
@app.route('/investors/dtypes', methods=['GET'])
def get_dtypes():
    
    investors_collection = db_investors['dtypes']
    
    message = investors_collection.find_one({'id': 'dtypes_raw'})
    return json.loads(json_util.dumps(message)), 200

@app.route('/investors/dtypes', methods=['POST'])
def create_dtypes():
    
    data = request.get_json()

    investors_collection = db_investors['dtypes']
    
    message = investors_collection.insert_one(data)
    if not message.acknowledged: return "FAILED", 400   
    return "cool", 200


# Método GET: para leitura de registro
# é necessário identificar o registro procurado. Os endpoints pedem
# pela chave de identificação. No caso do usuário 'user_name'
@app.route('/profile/<user_name>', methods=['GET'])
def get_user_profile(user_name):
    # Além do endereço do endpoint, também é definida uma função, assim ela
    # pode ser acessada por ambos os métodos (endpoint e função)

    # a partir do database de usuários (db_users) pegamos a collection
    # desejada (profile) e atribuímos a profile_collection
    profile_collection = db_users['profile']

    # O método find_one é usado para procurar por um registro, passando
    # um objeto como parâmetro que funcionará como filtro.
    # No exemplo a seguir procura-se pelo usuário cujo identificador
    # vale user_name (passado pelo endpoint) 
    message = profile_collection.find_one({"_user_name": user_name})

    # Caso o usuário solicitado não exista no banco de dados, então a variável
    # message não recebe nenhum valor, e entra na seguinte condição 
    if not message:
        # Como não encontrou o usuário procurado, então retorna a mensagem
        # informando erro, e o código 400 (código de erro genérico)
        return "FAILED TO GET PROFILE", 400

    # Se o usuário foi encontrado, então o registro é recebido pela variável
    # message, e retornado pela função junto com o código 200 (código de
    # sucesso genérico). O objeto encontrado é retornado em um JSON
    return json.loads(json_util.dumps(message)), 200

# Método POST: para inserção de registro
# é necessário enviar um objeto JSON representando o objeto a ser inserido
@app.route('/profile', methods=['POST'])
def create_user_profile():
    
    # Nos métodos de inserção é necessário enviar um objeto JSON junto ao
    # pedido http. Esse json é lido e armazenado na variável data
    data = request.get_json()

    # Algumas validações são feitas antes de inserir o registro
    # Nessa situação definiu-se importante verificar se o identificador
    # _user_name está no json enviado, caso ele não exista, a inserção
    # é cancelada, pois a falta desse campo prejudica os outros fluxos
    if '_user_name' not in data: return "MISSING USER NAME", 400

    # Essa variável foi usada para facilitar os testes durante o
    # desenvolvimento. Quando em teste, essa variável é definida como True
    # e então as verificações a seguir são ignoradas no teste
    if not isTesting:
        # Quando não em teste, os campos password, investor e email 
        # são obrigatórios
        if 'password' not in data: return "MISSING PASSWORD", 400
        if 'investor' not in data: return "MISSING INVESTOR PROFILE", 400    
        if 'email' not in data: return "MISSING EMAIL", 400

    # Atribuiu a coleção de usuários para a variável profile_collection
    profile_collection = db_users['profile']
    
    # O método insert_one é usado para inserir um registro, passando um
    # objeto como parâmetro. Este objeto contém os dados a serem inseridos
    message = profile_collection.insert_one(data)
    
    # Se a inserção não é bem sucedida, o objeto message não contém o
    # atributo acknowledged, e retorna mensagem de falha
    if not message.acknowledged: return "FAILED", 400   

    # O objeto inserido é lido no banco de dados, e atribuído a users
    users = get_user_profile(data['_user_name'])

    # O objeto users é retornado pelo endpoint, junto ao código de sucesso 
    return users[0], 200

# Método PUT: para atualização de registro
# é necessário identificar o registro a ser alterado. Os endpoints pedem
# pela chave de identificação. No caso do usuário 'user_name'
# Além do identificador do registro a ser alterado, também é necessário
# enviar um objeto JSON com as modificaçõe a serem feitas. Note que
# para alterações o objeto JSON precisa ter pelo menos um campo
# com chaves que indicam alteração, como $set 
@app.route('/profile/<user_name>', methods=['PUT'])
def update_user_profile(user_name):

    # Nos métodos de alteração é necessário enviar um objeto JSON junto ao
    # pedido http. Esse json é lido e armazenado na variável data
    data = request.get_json()

    # O objeto JSON é manipulado para adicionar os campos de atualização
    set_data = {
        "$set": data
    }

    # Atribuiu a coleção de usuários para a variável profile_collection
    profile_collection = db_users['profile']

    # Define-se um filtro com o identificador do usuário que será alterado
    profile_filter = {"_user_name" : user_name}
    # A função update_one atualiza um registro no banco, com base no filtro
    # enviado como parâmetro. Outro parâmetro enviado é o JSON com os 
    # dados que devem ser modificados
    message = profile_collection.update_one(profile_filter, set_data)
    
    # Se a atualização não é bem sucedida, o objeto message não contém o
    # atributo acknowledged, e retorna mensagem de falha
    if not message.acknowledged:
        # raise Error
        return "FAILED", 400

    # O objeto alterado é lido no banco de dados, e atribuído a users
    users = get_user_profile(data['_user_name'])

    # O objeto users é retornado pelo endpoint, junto ao código de sucesso 
    return users[0], 200

# Método DELETE: para remoção do registro no banco de dados
# é necessário identificar o registro a ser removido. Os endpoints pedem
# pela chave de identificação. No caso do usuário 'user_name'
@app.route('/profile/<user_name>', methods=['DELETE'])
def delete_user_profile(user_name):
    # Atribuiu a coleção de usuários para a variável profile_collection
    profile_collection = db_users['profile']

    # Define-se um filtro com o identificador do usuário que será removido
    profile_to_remove = {"_user_name" : user_name}
    # A função delete_one remove um registro no banco, com base no filtro
    # enviado como parâmetro
    message = profile_collection.delete_one(profile_to_remove)

    # Se a remoção não é bem sucedida, o objeto message não contém o
    # atributo acknowledged, e retorna mensagem de falha
    if not message.acknowledged:
        # raise Error
        return "FAILED", 400

    # Caso a remoção foi bem sucedida, retorna mensagem de sucesso, com
    # ocódigo de sucesso genérico 200
    return "USER DELETED", 200

# Endpoints para dados do database 'companies'
# Dados relacionados a empresas que serão analisadas pelo algoritmo
# Esses endpoints manipulam os dados da coleção raw_data
# São os dados puros enviados pelo usuário
# O identificador é _company_cnpj ou _company_id
@app.route('/company', methods=['POST'])
def create_company_raw_data():
    data = request.get_json()

    if '_company_cnpj' not in data: return "MISSING CNPJ", 400
    
    if not isTesting:  
        if '_user_name' not in data: return "MISSING USER NAME", 400
        if 'oficial_name' not in data: return "MISSING OFICIAL NAME", 400    

    company_raw_data_collection = db_companies['raw_data']
    company_filter = { '$or': [
        {'_company_cnpj': data['_company_cnpj']},
        {'_company_id': data['_company_id']}
    ]}

    # Na inserção de empresas, fazemos uma validação se o dado a ser inserido
    # já existe na base antes de efetivar a inserção
    already_exists = company_raw_data_collection.find_one(company_filter)

    # Se o registro já existe, então a empresa não pode ser cadastrada
    # novamente, e o endpoint retorna erro
    if already_exists:
        return "ALREADY INSERTED IN DATABASE", 400

    message = company_raw_data_collection.insert_one(data)    
    if not message.acknowledged:
        # raise Error
        return "FAILED", 400
    
    companies = get_company_raw_data(data['_company_id'])

    return companies[0], 200

# Método GET de empresas, com base no campo _company_id
@app.route('/company/<_company_id>', methods=['GET'])
def get_company_raw_data(_company_id):
    company_raw_data_collection = db_companies['raw_data']
    
    company_filter = {"_company_id" : int(_company_id)}
    message = company_raw_data_collection.find_one(company_filter)
    if not message:
        return "FAILED TO FIND COMPANY WHOSE ID IS "+_company_id, 400
    return json.loads(json_util.dumps(message)), 200

# Método GET de empresas, retorna todos os registros no database
@app.route('/company/all', methods=['GET'])
def get_all_company_raw_data():
    company_raw_data_collection = db_companies['raw_data']
    
    # O método find retorna todos os registros armazenados na coleção
    message = company_raw_data_collection.find()
    if not message:
        return "NO DATA IN COLLECTION RAW DATA IN COMPANIES DB", 400
    return json.loads(json_util.dumps(message)), 200

# Método PUT para alterar registro com base num _company_id
@app.route('/company/id/<_company_id>', methods=['PUT'])
def update_company_raw_data(_company_id):
    data = request.get_json()
    company_raw_data_collection = db_companies['raw_data']

    company_filter = {"_company_id" : int(_company_id)}
    company_found = company_raw_data_collection.find_one(company_filter)
    if not company_found:
        return "FAILED TO FIND COMPANY WHOSE ID IS "+_company_id, 400
    
    message = company_raw_data_collection.update_one(company_filter, data)    

    if not message.acknowledged: return "FAILED TO UPDATE", 400
    return "COMPANY IDENTIFICATION UPDATED", 200

# Método DELETE para remover registro com base num _company_id
@app.route('/company/<_company_id>', methods=['DELETE'])
def delete_company_raw_data(_company_id):
    company_raw_data_collection = db_companies['raw_data']
    company_to_remove = {"_company_id" : int(_company_id)}

    company_found = company_raw_data_collection.find_one(company_to_remove)
    if not company_found:
        return "FAILED TO FIND COMPANY WHOSE ID IS "+_company_id, 400
    
    message = company_raw_data_collection.delete_one(company_to_remove)
    if not message.acknowledged or message.deleted_count != 1:
        return "FAILED TO DELETE COMPANY IDENTIFICATION", 400
    return "COMPANY IDENTIFICATION DELETED", 200

# Endpoints para dados do database 'companies'
# Dados relacionados a empresas que serão analisadas pelo algoritmo
# Esses endpoints manipulam os dados da coleção metrics
# São os dados enviados pelo usuário após tratamento
# O identificador é _company_cnpj ou _company_id
@app.route('/company_metrics/<_company_id>', methods=['POST'])
def create_company_metrics(_company_id):
    data = request.get_json()

    # Certify all mandatory data will be set    
    if '_company_id' not in data: return "MISSING COMPANY ID", 400
    if '_user_name' not in data: return "MISSING USER NAME", 400
    
    company_metrics_collection = db_companies['metrics']
    company_filter = { '$or': [
        {'_company_id': int(_company_id)}
    ]}
    already_exists = company_metrics_collection.find_one(company_filter)
    if already_exists:
        return "ALREADY INSERTED IN DATABASE", 400

    message = company_metrics_collection.insert_one(data)    
    if not message.acknowledged:
        # raise Error
        return "FAILED TO INSERT METRICS", 400
    return "COMPANY IDENTIFICATION ADDED SUCCESSFULLY", 200

@app.route('/company_metrics/<_company_id>', methods=['GET'])
def get_company_metrics(_company_id):
    company_metrics_collection = db_companies['metrics']
    
    company_filter = {"_company_id" : int(_company_id)}
    message = company_metrics_collection.find_one(company_filter)
    if not message:
        return "FAILED TO FIND COMPANY WHOSE ID IS "+_company_id, 400
    return json.loads(json_util.dumps(message)), 200
    
@app.route('/company_metrics/all', methods=['GET'])
def get_all_company_metrics():
    company_metrics_collection = db_companies['metrics']
    
    message = company_metrics_collection.find()
    if not message:
        return "NO DATA IN COLLECTION METRICS IN COMPANIES DB", 400
    return json.loads(json_util.dumps(message)), 200

@app.route('/company_metrics/<_company_id>', methods=['PUT'])
def update_company_metrics(_company_id):
    data = request.get_json()
    company_metrics_collection = db_companies['metrics']

    company_filter = {"_company_id" : int(_company_id)}
    company_found = company_metrics_collection.find_one(company_filter)
    if not company_found:
        return "FAILED TO FIND COMPANY WHOSE ID IS "+_company_id, 400
    
    message = company_metrics_collection.update_one(company_filter, data)    
    if not message.acknowledged: return "FAILED TO UPDATE", 400
    return "COMPANY IDENTIFICATION UPDATED", 200

@app.route('/company_metrics/<_company_id>', methods=['DELETE'])
def delete_company_metrics(_company_id):
    company_metrics_collection = db_companies['metrics']
    company_to_remove = {"_company_id" : int(_company_id)}

    company_found = company_metrics_collection.find_one(company_to_remove)
    if not company_found:
        return "FAILED TO FIND COMPANY WHOSE ID IS "+_company_id, 400
    
    message = company_metrics_collection.delete_one(company_to_remove)
    if not message.acknowledged or message.deleted_count != 1:
        return "FAILED TO DELETE COMPANY IDENTIFICATION", 400
    return "COMPANY IDENTIFICATION DELETED", 200

# Endpoints para dados do database 'investors_theory'
# Dados relacionados a tese de investimento
# Esses endpoints manipulam os dados da coleção historic_data
# São os dados enviados pelo usuário investidor, ou seja, base histórica
# O identificador é _historic_id
# Outra maneira de identificação é através do par usuário e nome da teoria
@app.route('/investors_theory/historic_data', methods=['POST'])
def create_investors_theory_historic_data():
    data = request.get_json()

    # Certify all mandatory data will be set    
    if '_user_name' not in data: return "MISSING USER NAME", 400
    
    if not isTesting:
        # Quando fora de ambiente de teste, o usuário relacionado com a tese
        # é validado na base de usuários antes de prosseguir
        profile_collection = db_users['profile']
        user_added = profile_collection.find_one({"_user_name": data['_user_name']})
        if not user_added:
            return "USER IS NOT IN DATABASE, PLEASE ADD USER FIRST"
    
    investors_theory_collection = db_investors['historic_data']

    most_recent_theory = investors_theory_collection.find_one(sort=[("_historic_id", -1)])

    # Implementa lógica para incrementar o id da tese, os ids da tese não são
    # passados pelo usuário, eles são definidos automaticamente
    # Para definir o id da tese a ser inserida, recebe o valor mais alto
    # cadastrado até então, e incrementa 1
    if most_recent_theory: highest_historic_id = most_recent_theory["_historic_id"]
    else: highest_historic_id = 0
    theory_id = highest_historic_id + 1
    data["_historic_id"] = theory_id

    # Filtro para encontrar uma tese do mesmo usuário investidor com o
    # mesmo nome. Um investidor pode cadastrar mais de uma tese, mas cada
    # uma deve ter um nome único, podendo ser igual para usuários diferentes
    investor_theory_filter = { '$and': [
        {'_user_name': data['_user_name']},        
        {'_theory_name': data['_theory_name']}
    ]}
    already_exists = investors_theory_collection.find_one(investor_theory_filter)
    if already_exists:
        return "ALREADY INSERTED IN DATABASE", 400

    message = investors_theory_collection.insert_one(data)    
    if not message.acknowledged:
        # raise Error
        return "FAILED TO INSERT THEORY", 400
        
    success = get_investors_theory_historic_data(data['_user_name'], data['_theory_name'])

    return success[0], 200

# Método GET para leitura de uma tese com base no valor do par usuário e
# nome da teoria
@app.route('/investors_theory/historic_data/<_user_name>/<_theory_name>', methods=['GET'])
def get_investors_theory_historic_data(_user_name, _theory_name):
    investors_theory_collection = db_investors['historic_data']
    
    investor_theory_filter = {
        "_user_name" : _user_name,
        "_theory_name" : _theory_name
    }
    message = investors_theory_collection.find_one(investor_theory_filter)
    
    return json.loads(json_util.dumps(message)), 200

@app.route('/investors_theory/historic_data/<_user_name>/<_theory_name>', methods=['PUT'])
def update_investors_theory_historic_data(_user_name, _theory_name):
    data = request.get_json()
    investors_theory_collection = db_investors['historic_data']

    investor_theory_filter = {
        "_user_name" : _user_name,
        "_theory_name" : _theory_name
    }
    theory_found = investors_theory_collection.find_one(investor_theory_filter)
    if not theory_found:
        return "FAILED TO FIND THEORY", 400
    
    message = investors_theory_collection.update_one(investor_theory_filter, data)    
    if not message.acknowledged:
        return "FAILED TO UPDATE THEORY", 400

    success = get_investors_theory_historic_data(_user_name, _theory_name)

    return success[0], 200

@app.route('/investors_theory/historic_data/<_user_name>/<_theory_name>', methods=['DELETE'])
def delete_investors_theory_historic_data(_user_name, _theory_name):
    investors_theory_collection = db_investors['historic_data']
    theory_to_remove = {
        "_user_name" : _user_name,
        "_theory_name" : _theory_name
    }

    theory_found = investors_theory_collection.find_one(theory_to_remove)
    if not theory_found:
        return "FAILED TO FIND THEORY", 400
    
    message = investors_theory_collection.delete_one(theory_to_remove)
    if not message.acknowledged or message.deleted_count != 1:
        return "FAILED TO DELETE THEORY", 400
    return "THEORY {} DELETED".format(_theory_name), 200

# Endpoints para dados do database 'investors_theory'
# Dados relacionados a tese de investimento
# Esses endpoints manipulam os dados da coleção historic_tratado
# São os dados enviados pelo usuário investidor, após serem tratados
# Esses dados que serão submetidos a modelagem
# O identificador é _historic_id
# Outra maneira de identificação é através do par usuário e nome da teoria
@app.route('/investors_theory/historic_tratado', methods=['POST'])
def create_investors_theory_historic_tratado():
    data = request.get_json()

    # Certify all mandatory data will be set    
    if '_user_name' not in data: return "MISSING USER NAME", 400
    
    if not isTesting:
        profile_collection = db_users['profile']
        user_added = profile_collection.find_one({"_user_name": data['_user_name']})
        if not user_added:
            return "USER IS NOT IN DATABASE, PLEASE ADD USER FIRST"
    
    investors_theory_collection = db_investors['historic_tratado']

    most_recent_theory = investors_theory_collection.find_one(sort=[("_historic_id", -1)])
    if most_recent_theory: highest_historic_id = most_recent_theory["_historic_id"]
    else: highest_historic_id = 0
    theory_id = highest_historic_id + 1
    data["_historic_id"] = theory_id

    investor_theory_filter = { '$and': [
        {'_user_name': data['_user_name']},        
        {'_theory_name': data['_theory_name']}
    ]}
    already_exists = investors_theory_collection.find_one(investor_theory_filter)
    if already_exists:
        return "ALREADY INSERTED IN DATABASE", 400

    message = investors_theory_collection.insert_one(data)    
    if not message.acknowledged:
        # raise Error
        return "FAILED TO INSERT THEORY", 400
        
    success = get_investors_theory_historic_tratado(data['_user_name'], data['_theory_name'])

    return success[0], 200

@app.route('/investors_theory/historic_tratado/<_user_name>/<_theory_name>', methods=['GET'])
def get_investors_theory_historic_tratado(_user_name, _theory_name):
    investors_theory_collection = db_investors['historic_tratado']
    
    investor_theory_filter = {
        "_user_name" : _user_name,
        "_theory_name" : _theory_name
    }
    message = investors_theory_collection.find_one(investor_theory_filter)
    
    return json.loads(json_util.dumps(message)), 200

@app.route('/investors_theory/historic_tratado/<_user_name>/<_theory_name>', methods=['PUT'])
def update_investors_theory_historic_tratado(_user_name, _theory_name):
    data = request.get_json()
    investors_theory_collection = db_investors['historic_tratado']

    investor_theory_filter = {
        "_user_name" : _user_name,
        "_theory_name" : _theory_name
    }
    theory_found = investors_theory_collection.find_one(investor_theory_filter)
    if not theory_found:
        return "FAILED TO FIND THEORY", 400
    
    message = investors_theory_collection.update_one(investor_theory_filter, data)    
    if not message.acknowledged:
        return "FAILED TO UPDATE THEORY", 400

    success = get_investors_theory_historic_tratado(_user_name, _theory_name)

    return success[0], 200

@app.route('/investors_theory/historic_tratado/<_user_name>/<_theory_name>', methods=['DELETE'])
def delete_investors_theory_historic_tratado(_user_name, _theory_name):
    investors_theory_collection = db_investors['historic_tratado']
    theory_to_remove = {
        "_user_name" : _user_name,
        "_theory_name" : _theory_name
    }

    theory_found = investors_theory_collection.find_one(theory_to_remove)
    if not theory_found:
        return "FAILED TO FIND THEORY", 400
    
    message = investors_theory_collection.delete_one(theory_to_remove)
    if not message.acknowledged or message.deleted_count != 1:
        return "FAILED TO DELETE THEORY", 400
    return "THEORY {} DELETED".format(_theory_name), 200

@app.route('/investors_theory/historic_filtrado', methods=['POST'])
def create_investors_theory_historic_filtrado():
    data = request.get_json()

    # Certify all mandatory data will be set    
    if '_user_name' not in data: return "MISSING USER NAME", 400
    
    if not isTesting:
        profile_collection = db_users['profile']
        user_added = profile_collection.find_one({"_user_name": data['_user_name']})
        if not user_added:
            return "USER IS NOT IN DATABASE, PLEASE ADD USER FIRST"
    
    investors_theory_collection = db_investors['historic_filtrado']

    most_recent_theory = investors_theory_collection.find_one(sort=[("_historic_id", -1)])
    if most_recent_theory: highest_historic_id = most_recent_theory["_historic_id"]
    else: highest_historic_id = 0
    theory_id = highest_historic_id + 1
    data["_historic_id"] = theory_id

    investor_theory_filter = { '$and': [
        {'_user_name': data['_user_name']},        
        {'_theory_name': data['_theory_name']}
    ]}
    already_exists = investors_theory_collection.find_one(investor_theory_filter)
    if already_exists:
        return "ALREADY INSERTED IN DATABASE", 400

    message = investors_theory_collection.insert_one(data)    
    if not message.acknowledged:
        # raise Error
        return "FAILED TO INSERT THEORY", 400
        
    success = get_investors_theory_historic_filtrado(data['_user_name'], data['_theory_name'])

    return success[0], 200

@app.route('/investors_theory/historic_filtrado/<_user_name>/<_theory_name>', methods=['GET'])
def get_investors_theory_historic_filtrado(_user_name, _theory_name):
    investors_theory_collection = db_investors['historic_filtrado']
    
    investor_theory_filter = {
        "_user_name" : _user_name,
        "_theory_name" : _theory_name
    }
    message = investors_theory_collection.find_one(investor_theory_filter)
    
    return json.loads(json_util.dumps(message)), 200

@app.route('/investors_theory/historic_filtrado/<_user_name>/<_theory_name>', methods=['PUT'])
def update_investors_theory_historic_filtrado(_user_name, _theory_name):
    data = request.get_json()
    investors_theory_collection = db_investors['historic_filtrado']

    investor_theory_filter = {
        "_user_name" : _user_name,
        "_theory_name" : _theory_name
    }
    theory_found = investors_theory_collection.find_one(investor_theory_filter)
    if not theory_found:
        return "FAILED TO FIND THEORY", 400
    
    message = investors_theory_collection.update_one(investor_theory_filter, data)    
    if not message.acknowledged:
        return "FAILED TO UPDATE THEORY", 400

    success = get_investors_theory_historic_filtrado(_user_name, _theory_name)

    return success[0], 200

@app.route('/investors_theory/historic_filtrado/<_user_name>/<_theory_name>', methods=['DELETE'])
def delete_investors_theory_historic_filtrado(_user_name, _theory_name):
    investors_theory_collection = db_investors['historic_filtrado']
    theory_to_remove = {
        "_user_name" : _user_name,
        "_theory_name" : _theory_name
    }

    theory_found = investors_theory_collection.find_one(theory_to_remove)
    if not theory_found:
        return "FAILED TO FIND THEORY", 400
    
    message = investors_theory_collection.delete_one(theory_to_remove)
    if not message.acknowledged or message.deleted_count != 1:
        return "FAILED TO DELETE THEORY", 400
    return "THEORY {} DELETED".format(_theory_name), 200

# Endpoints para dados do database 'companies' collection 'from_csv'
# Dados relacionados a empresas que serão analisadas pelo algoritmo
# Esses endpoints manipulam os dados da coleção raw_data
# São os dados puros enviados pelo usuário
# O identificador é _company_cnpj ou _company_id
@app.route('/company/from_csv', methods=['POST'])
def create_company_from_csv():
    data = request.get_json()

    if '_company_cnpj' not in data: return "MISSING CNPJ", 400
    
    if not isTesting:
        # Certify all mandatory data will be set    
        if '_user_name' not in data: return "MISSING USER NAME", 400
        if 'oficial_name' not in data: return "MISSING OFICIAL NAME", 400    

    company_from_csv_collection = db_companies['from_csv']
    company_filter = { '$or': [
        {'_company_cnpj': data['_company_cnpj']},
        {'_company_cnpj': data['_company_cnpj']}
    ]}
    already_exists = company_from_csv_collection.find_one(company_filter)
    if already_exists:
        return "ALREADY INSERTED IN DATABASE", 400

    message = company_from_csv_collection.insert_one(data)    
    if not message.acknowledged:
        # raise Error
        return "FAILED", 400
    
    companies = get_company_from_csv_by_cnpj(data['_company_cnpj'])

    return companies[0], 200

@app.route('/company/from_csv/cnpj/<_company_cnpj>', methods=['GET'])
def get_company_from_csv_by_cnpj(_company_cnpj):
    company_from_csv_collection = db_companies['from_csv']
    
    company_filter = {"_company_cnpj" : _company_cnpj}
    message = company_from_csv_collection.find_one(company_filter)
    if not message:
        return "FAILED TO FIND COMPANY WHOSE ID IS "+_company_cnpj, 400
    return json.loads(json_util.dumps(message)), 200

@app.route('/company/from_csv/cnpj/<_company_cnpj>', methods=['PUT'])
def update_company_from_csv_by_cnpj(_company_cnpj):
    data = request.get_json()
    company_from_csv_collection = db_companies['from_csv']

    company_filter = {"_company_cnpj" : _company_cnpj}
    company_found = company_from_csv_collection.find_one(company_filter)
    if not company_found:
        return "FAILED TO FIND COMPANY WHOSE ID IS "+_company_cnpj, 400
    
    message = company_from_csv_collection.update_one(company_filter, data)    

    if not message.acknowledged: return "FAILED TO UPDATE", 400
    return "COMPANY IDENTIFICATION UPDATED", 200

@app.route('/company/from_csv/cnpj/<_company_cnpj>', methods=['DELETE'])
def delete_company_from_csv_by_cnpj(_company_cnpj):
    company_from_csv_collection = db_companies['from_csv']

    company_to_remove = {
        "_company_cnpj" : _company_cnpj
    }

    company_found = company_from_csv_collection.find_one(company_to_remove)
    if not company_found:
        return "FAILED TO FIND THEORY", 400
    
    message = company_from_csv_collection.delete_one(company_to_remove)
    if not message.acknowledged or message.deleted_count != 1:
        return "FAILED TO DELETE THEORY", 400
    return "COMPANY {} DELETED".format(_company_cnpj), 200

# Endpoints para dados do database 'investors_theory'
# collection 'parameters_and_weights'
# São os dados manipulados pelo sistema
# O identificador é _company_cnpj ou _company_id
@app.route('/investors_theory', methods=['POST'])
def create_investors_theory():
    data = request.get_json()

    # Certify all mandatory data will be set    
    if '_user_name' not in data: return "MISSING USER NAME", 400
    
    profile_collection = db_users['profile']
    user_added = profile_collection.find_one({"_user_name": data['_user_name']})
    if not user_added:
        return "USER IS NOT IN DATABASE, PLEASE ADD USER FIRST"
    
    investors_theory_collection = db_investors['parameters_and_weights']

    most_recent_theory = investors_theory_collection.find_one(sort=[("_theory_id", -1)])
    if most_recent_theory: highest_theory_id = most_recent_theory["_theory_id"]
    else: highest_theory_id = 0
    theory_id = highest_theory_id + 1
    data["_theory_id"] = theory_id

    investor_theory_filter = { '$and': [
        {'_user_name': data['_user_name']},        
        {'_theory_name': data['_theory_name']}
    ]}
    already_exists = investors_theory_collection.find_one(investor_theory_filter)
    if already_exists:
        return "ALREADY INSERTED IN DATABASE", 400

    message = investors_theory_collection.insert_one(data)    
    if not message.acknowledged:
        # raise Error
        return "FAILED TO INSERT THEORY", 400
    success = {
        "message": "THEORY ADDED SUCCESSFULLY",
        "_theory_id": theory_id
    }
    return success, 200

@app.route('/investors_theory/<_theory_id>', methods=['GET'])
def get_investors_theory(_theory_id):
    investors_theory_collection = db_investors['parameters_and_weights']
    
    investor_theory_filter = {"_theory_id" : int(_theory_id)}
    message = investors_theory_collection.find_one(investor_theory_filter)
    if not message:
        return "FAILED TO FIND THEORY WHOSE ID IS "+_theory_id, 400
    return json.loads(json_util.dumps(message)), 200
    
@app.route('/investors_theory/all', methods=['GET'])
def get_all_investors_theory():
    investors_theory_collection = db_investors['parameters_and_weights']
    
    message = investors_theory_collection.find()
    if not message:
        return "NO DATA IN COLLECTION PARAMETERS IN COMPANIES DB", 400
    return json.loads(json_util.dumps(message)), 200

@app.route('/investors_theory/<_theory_id>', methods=['PUT'])
def update_investors_theory(_theory_id):
    data = request.get_json()
    investors_theory_collection = db_investors['parameters_and_weights']

    investor_theory_filter = {"_theory_id" : int(_theory_id)}
    theory_found = investors_theory_collection.find_one(investor_theory_filter)
    if not theory_found:
        return "FAILED TO FIND THEORY WHOSE ID IS "+_theory_id, 400
    
    message = investors_theory_collection.update_one(investor_theory_filter, data)    
    if not message.acknowledged:
        return "FAILED TO UPDATE THEORY WHOSE ID IS "+_theory_id, 400
    return "THEORY "+_theory_id+" UPDATED", 200

@app.route('/investors_theory/<_theory_id>', methods=['DELETE'])
def delete_investors_theory(_theory_id):
    investors_theory_collection = db_investors['parameters_and_weights']
    theory_to_remove = {"_theory_id" : int(_theory_id)}

    theory_found = investors_theory_collection.find_one(theory_to_remove)
    if not theory_found:
        return "FAILED TO FIND THEORY WHOSE ID IS "+_theory_id, 400
    
    message = investors_theory_collection.delete_one(theory_to_remove)
    if not message.acknowledged or message.deleted_count != 1:
        return "FAILED TO DELETE THEORY WHOSE ID IS "+_theory_id, 400
    return "THEORY "+_theory_id+" DELETED", 200

# Endpoints para dados do database 'results'
# collection 'results_and_comments'
# São os dados gerados pelo algoritmo após a análise da empresa
# O identificador é _company_cnpj ou _company_id
@app.route('/results', methods=['POST'])
def create_results():
    data = request.get_json()

    # Certify all mandatory data will be set    
    if '_theory_name' not in data: return "MISSING THEORY NAME", 400
    if '_company_cnpj' not in data: return "MISSING COMPANY CNPJ", 400
    if 'approved' not in data: return "MISSING RESULT APPROVED", 400
    
    if not isTesting:
        investors_theory_collection = db_investors['parameters_and_weights']
        theory_filter = {"_theory_id": data['_theory_id']}
        theory_added = investors_theory_collection.find_one(theory_filter)
        if not theory_added:
            return "THEORY IS NOT IN DATABASE, PLEASE ADD THEORY FIRST"
        
        company_metrics_collection = db_companies['metrics']
        company_filter = {"_company_id" : data["_company_id"]}
        company_added = company_metrics_collection.find_one(company_filter)
        if not company_added:
            return "COMPANY IS NOT IN DATABASE, PLEASE ADD COMPANY FIRST"
    
    results_collection = db_results['results_and_comments']

    investor_theory_filter = { '$and': [
        {'_theory_name': data['_theory_name']},        
        {'_company_cnpj': data['_company_cnpj']}
    ]}
    already_exists = results_collection.find_one(investor_theory_filter)
    if already_exists:
        return "ALREADY INSERTED IN DATABASE", 400

    message = results_collection.insert_one(data)    
    if not message.acknowledged:
        return "FAILED TO INSERT RESULT", 400
    
    success = get_results(data['_theory_name'], data['_company_cnpj'])

    return success[0], 200

@app.route('/results/single/<_theory_name>/<_company_cnpj>', methods=['GET'])
def get_results(_theory_name, _company_cnpj):
    results_collection = db_results['results_and_comments']
    
    results_filter = {
        "_theory_name" : _theory_name,
        "_company_cnpj" : _company_cnpj
    }
    message = results_collection.find_one(results_filter)
    if not message:
        return "FAILED TO FIND RESULTS FOR THEORY ID "+_theory_name+" AND COMPANY ID "+_company_cnpj, 400
    return json.loads(json_util.dumps(message)), 200

@app.route('/results/theory/<_theory_id>', methods=['GET'])
def get_results_theory(_theory_id):
    results_collection = db_results['results_and_comments']
    
    results_filter = {"_theory_id" : int(_theory_id)}
    message = results_collection.find(results_filter)
    if not message:
        return "FAILED TO FIND RESULTS FOR THEORY ID "+_theory_id, 400
    return json.loads(json_util.dumps(message)), 200

@app.route('/results/company/<_company_id>', methods=['GET'])
def get_results_company(_company_id):
    results_collection = db_results['results_and_comments']
    
    results_filter = {"_company_id" : int(_company_id)}
    message = results_collection.find(results_filter)
    if not message:
        return "FAILED TO FIND RESULTS FOR COMPANY ID "+_company_id, 400
    return json.loads(json_util.dumps(message)), 200
    
@app.route('/results/all', methods=['GET'])
def get_all_results():
    results_collection = db_results['results_and_comments']
    
    message = results_collection.find()
    if not message:
        return "NO DATA IN COLLECTION PARAMETERS IN RESULTS DB", 400
    return json.loads(json_util.dumps(message)), 200

@app.route('/results/<theory_name>/<company_cnpj>', methods=['PUT'])
def update_results(theory_name, company_cnpj):
    data = request.get_json()
    results_collection = db_results['results_and_comments']

    results_filter = {
        "_theory_name" : theory_name,
        "_company_cnpj" : company_cnpj       
    }
    theory_found = results_collection.find_one(results_filter)
    if not theory_found:
        return "FAILED TO FIND RESULTS FOR THEORY ID "+theory_name+" AND COMPANY ID "+company_cnpj, 400
    
    message = results_collection.update_one(results_filter, data)    
    if not message.acknowledged:
        return "FAILED TO UPDATE RESULTS FOR THEORY ID "+theory_name+" AND COMPANY ID "+company_cnpj, 400
    return "RESULTS FOR THEORY "+theory_name+" COMPANY "+company_cnpj+" UPDATED", 200

@app.route('/results/single/<theory_name>/<company_cnpj>', methods=['DELETE'])
def delete_results(theory_name, company_cnpj):
    results_collection = db_results['results_and_comments']
    results_filter = {
        "_theory_name" : theory_name,
        "_company_cnpj" : company_cnpj        
    }
    theory_found = results_collection.find_one(results_filter)
    if not theory_found:
        return "FAILED TO FIND RESULTS FOR THEORY ID "+theory_name+" AND COMPANY ID "+company_cnpj, 400
    
    message = results_collection.delete_one(results_filter)
    if not message.acknowledged or message.deleted_count != 1:
        return "FAILED TO DELETE RESULTS FOR THEORY ID "+theory_name+" AND COMPANY ID "+company_cnpj, 400
    return "RESULTS FOR THEORY "+theory_name+" COMPANY "+company_cnpj+" DELETED", 200

@app.route('/results/theory/<_theory_id>', methods=['DELETE'])
def delete_results_theory(_theory_id):
    results_collection = db_results['results_and_comments']
    
    results_filter = {"_theory_id" : int(_theory_id)}
    result_found = results_collection.find(results_filter)
    if not result_found:
        return "FAILED TO FIND RESULTS FOR THEORY ID "+_theory_id, 400
    
    message = results_collection.delete_many(results_filter)
    if not message.acknowledged or message.deleted_count < 1:
        return "FAILED TO DELETE RESULTS FOR THEORY ID "+_theory_id, 400
    return "RESULTS FOR THEORY "+_theory_id+" DELETED", 200

@app.route('/results/company/<_company_id>', methods=['DELETE'])
def delete_results_company(_company_id):
    results_collection = db_results['results_and_comments']
    
    results_filter = {"_company_id" : int(_company_id)}
    result_found = results_collection.find(results_filter)
    if not result_found:
        return "FAILED TO FIND RESULTS FOR COMPANY ID "+_company_id, 400
    
    message = results_collection.delete_many(results_filter)
    if not message.acknowledged or message.deleted_count < 1:
        return "FAILED TO DELETE RESULTS FOR COMPANY ID "+_company_id, 400
    return "RESULTS FOR COMPANY "+_company_id+" DELETED", 200
    
# Endpoints usados para gerar os modelos fornecidos ao usuário investidor
# São fornecidos dois modelos, um vazio e outro com dados fictícios 
# preenchidos para exemplificação
@app.route('/example_investor_data/empty', methods=['GET'])
def get_empty_example_investor():
    example_collection = db_investors['examples']
    message = example_collection.find_one({"_example_id": 1, "name": "Empty example"})

    if not message: return "FAILED TO GET EMPTY EXAMPLE", 400
    return json.loads(json_util.dumps(message)), 200       

@app.route('/example_investor_data/filled', methods=['GET'])
def get_filled_example_investor():
    example_collection = db_investors['examples']
    message = example_collection.find_one({"_example_id": 2, "name": "Filled example"})

    if not message: return "FAILED TO GET FILLED EXAMPLE", 400
    return json.loads(json_util.dumps(message)), 200        

@app.route('/example_investor_data', methods=['POST'])
def create_examples_investor():
    data = request.get_json()

    # Certify all mandatory data will be set
    if '_example_id' not in data: return "MISSING EXAMPLE ID", 400
    if 'name' not in data: return "MISSING NAME", 400

    example_collection = db_investors['examples']
    message = example_collection.insert_one(data)
    
    if not message.acknowledged: return "FAILED", 400    
    return "SUCCESS INSERTING EXAMPLE", 200

if __name__ == "__main__":    
    # Atribui os databases às variáveis 
    db_users = get_database('users')
    db_companies = get_database('companies')
    db_investors = get_database('investors_theories')
    db_results = get_database('results')

    app.run()