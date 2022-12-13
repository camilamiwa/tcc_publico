Para testar os endpoints, abra um outro shell e rode os comandos a seguir

Pymongo CRUD documentation
https://www.mongodb.com/docs/manual/crud/


:-:-:-: USERS - PROFILE

To GET:
curl -i -X GET http://localhost:5000/profile/<USER_NAME>

To run DELETE:
curl -i -X DELETE http://localhost:5000/profile/<USER_NAME>

To run POST:
curl -i -H "Content-Type: application/json" -X POST -d @<PATH_FILE_NAME>.json http://localhost:5000/profile

To PUT (UPDATE):
curl -i -H "Content-Type: application/json" -X PUT -d @<PATH_FILE_NAME>.json http://localhost:5000/profile/<USER_NAME>


:-:-:-: COMPANIES - RAW DATA

To run POST:
curl -i -H "Content-Type: application/json" -X POST -d @<PATH_FILE_NAME>.json http://localhost:5000/company

curl -i -H "Content-Type: application/json" -X POST -d @json_files/post_company_raw_data.json http://localhost:5000/company

To GET:
curl -i -X GET http://localhost:5000/company/<COMPANY_ID>

To GET all data:
curl -i -X GET http://localhost:5000/company/all

To PUT (UPDATE):
curl -i -H "Content-Type: application/json" -X PUT -d @<PATH_FILE_NAME>.json http://localhost:5000/company/<COMPANY_ID>

curl -i -H "Content-Type: application/json" -X PUT -d @json_files/put_company_raw_data.json http://localhost:5000/company/1

To run DELETE:
curl -i -X DELETE http://localhost:5000/company/<COMPANY_ID>


:-:-:-: COMPANIES - METRICS

To run POST:
curl -i -H "Content-Type: application/json" -X POST -d @<PATH_FILE_NAME>.json http://localhost:5000/company_metrics/<COMPANY_ID>

curl -i -H "Content-Type: application/json" -X POST -d @json_files/post_company_metrics.json http://localhost:5000/company_metrics/1

To GET:
curl -i -X GET http://localhost:5000/company_metrics/<COMPANY_ID>

To GET all:
curl -i -X GET http://localhost:5000/company_metrics/all

To PUT (UPDATE):
curl -i -H "Content-Type: application/json" -X PUT -d @<PATH_FILE_NAME>.json http://localhost:5000/company_metrics/<COMPANY_ID>

curl -i -H "Content-Type: application/json" -X PUT -d @json_files/put_company_metrics.json http://localhost:5000/company_metrics/1

To run DELETE:
curl -i -X DELETE http://localhost:5000/company_metrics/<COMPANY_ID>




:-:-:-: INVESTORS - PARAMETERS

To run POST:
curl -i -H "Content-Type: application/json" -X POST -d @<PATH_FILE_NAME>.json http://localhost:5000/investors_theory/<THEORY_ID>

curl -i -H "Content-Type: application/json" -X POST -d @json_files/post_investor_theory.json http://localhost:5000/investors_theory

To GET:
curl -i -X GET http://localhost:5000/investors_theory/<THEORY_ID>

To GET all:
curl -i -X GET http://localhost:5000/investors_theory/all

To PUT (UPDATE):
curl -i -H "Content-Type: application/json" -X PUT -d @<PATH_FILE_NAME>.json http://localhost:5000/investors_theory/<THEORY_ID>

curl -i -H "Content-Type: application/json" -X PUT -d @json_files/put_investor_theory.json http://localhost:5000/investors_theory/1

To run DELETE:
curl -i -X DELETE http://localhost:5000/investors_theory/<THEORY_ID>




:-:-:-: RESULTS

To run POST:
curl -i -H "Content-Type: application/json" -X POST -d @<PATH_FILE_NAME>.json http://localhost:5000/results

curl -i -H "Content-Type: application/json" -X POST -d @json_files/post_results.json http://localhost:5000/results

To GET single:
curl -i -X GET http://localhost:5000/results/single/<THEORY_ID>/<COMPANY_ID>

To GET by theory:
curl -i -X GET http://localhost:5000/results/theory/<THEORY_ID>

To GET by company:
curl -i -X GET http://localhost:5000/results/company/<COMPANY_ID>

To GET all:
curl -i -X GET http://localhost:5000/results/all

To PUT (UPDATE):
curl -i -H "Content-Type: application/json" -X PUT -d @<PATH_FILE_NAME>.json http://localhost:5000/results/<THEORY_ID>

curl -i -H "Content-Type: application/json" -X PUT -d @json_files/put_results.json http://localhost:5000/results/1

To run DELETE single:
curl -i -X DELETE http://localhost:5000/results/single/<THEORY_ID>/<COMPANY_ID>

To run DELETE by theory:
curl -i -X DELETE http://localhost:5000/results/theory/<THEORY_ID>

To run DELETE by company:
curl -i -X DELETE http://localhost:5000/results/company/<COMPANY_ID>