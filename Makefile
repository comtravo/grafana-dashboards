#!make

GENERATE_DOCS_COMMAND:=terraform-docs --sort-inputs-by-required markdown --no-escape . > README.md

build:
	@docker-compose build

develop-scripts:
	@docker-compose -f ./docker-compose.yml -f ./docker-compose.develop.yml run --rm grafana_dashboard_generator bash

develop-module:
	@docker-compose -f ./docker-compose.yml -f ./docker-compose.develop.yml run --rm grafana_terraform_module bash

init:
	@pip install -r requirements.txt

fmt-py:
	@black .

lint-py:
	@black --check .

fmt-go:
	@terraform fmt -recursive
	@find . -name '*.go' | xargs gofmt -w -s

lint-go:
	@terraform fmt -check -recursive -diff=true
	@test -z $(shell find . -type f -name '*.go' | xargs gofmt -l)
	@tflint

clean-state:
	@find . -type f -name 'terraform.tfstate*' | xargs rm -rf
	@find . -type d -name '.terraform' | xargs rm -rf

generate-docs: fmt-go lint-go
	@$(shell $(GENERATE_DOCS_COMMAND))
	@find terraform_modules -maxdepth 1 -type d -not -path 'terraform_modules' -exec sh -c 'cd {} && $(GENERATE_DOCS_COMMAND)' ';'

test-integration:
	@cd test/integration && go test
