#!make

build:
	@docker-compose build

develop-scripts:
	@docker-compose -f ./docker-compose.yml -f ./docker-compose.develop.yml run --rm grafana_dashboard_generator bash

develop-module:
	@docker-compose -f ./docker-compose.yml -f ./docker-compose.develop.yml run --rm grafana_terraform_module bash

init:
	@pip install -r requirements.txt

fmt:
	@black .
	@terraform fmt -recursive

lint:
	@black --check .
