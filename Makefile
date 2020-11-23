#!make

build:
	@docker-compose build

develop:
	@docker-compose -f ./docker-compose.yml -f ./docker-compose.develop.yml run --rm grafana_dashboard_generator bash

init:
	@pip install -r requirements.txt

fmt:
	@black *.py
