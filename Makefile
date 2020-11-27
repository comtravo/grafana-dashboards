#!make

GENERATE_DOCS_COMMAND:=terraform-docs markdown . > README.md

build:
	@docker-compose build

develop:
	@docker-compose -f ./docker-compose.yml -f ./docker-compose.develop.yml run --rm workhorse bash ; docker-compose down -v

test-docker:
	@docker-compose -f ./docker-compose.yml -f ./docker-compose.develop.yml run --rm workhorse make test; docker-compose down -v

init:
	@pip3 install -r requirements.txt

fmt-py:
	@black .

fmt-go:
	@terraform fmt -recursive
	@find . -name '*.go' | xargs gofmt -w -s

fmt: fmt-go fmt-py

lint-py:
	@black --check .

lint-go:
	@terraform fmt -check -recursive -diff=true
	@test -z $(shell find . -type f -name '*.go' | xargs gofmt -l)

lint: lint-py lint-go

clean-state:
	@find . -type f -name 'terraform.tfstate*' | xargs rm -rf
	@find . -type f -name 'dashboard.json' | xargs rm -rf
	@find . -type d -name '.terraform' | xargs rm -rf

clean-py:
	@find . -type f -name '*.pyc' | xargs rm -rf

clean: clean-py clean-state


generate-docs: fmt-go lint-go
	@find terraform_modules -maxdepth 1 -type d -not -path 'terraform_modules' -exec sh -c 'cd {} && $(GENERATE_DOCS_COMMAND)' ';'

test-integration:
	@cd test/integration && go test

test: test-integration

.PHONY: test
