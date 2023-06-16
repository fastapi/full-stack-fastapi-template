include .env
export
.DEFAULT_GOAL := help

.PHONY: help up up-quiet down build bash test lint cov report format migrate generate-migration

help: Makefile
	@sed -n 's/^##//p' $< | cat

## up                       | Build and run the application
up:
	docker compose up

## up-quiet                 | Build and run the application in background
up-quiet:
	docker compose up -d

## down                     | Stop the application, notebook server, and code server
down:
	docker compose down
	docker compose rm

## build                    | Build the application images
build:
	$(MAKE) down
	DOCKER_BUILDKIT=1 docker compose build

## bash                     | Access to API bash
bash:
	docker compose exec api bash

## test   		  | Run unit tests
test:
	sh ./scripts/test.sh app/tests/$(TESTS_DIR)

## lint                     | Run lint checks
lint:
	sh ./app/scripts/lint.sh

## cov                      | Run coverage
cov:
	sh ./app/scripts/cov.sh

## report                   | Run coverage report
report:
	sh ./app/scripts/test-cov-html.sh

## format                   | Run formats
format:
	sh ./app/scripts/format.sh

## migrate                  | Run migrations
migrate:
	docker compose -f docker-compose.yml exec -T api alembic upgrade head

## generate-migration       | Generate migration template
generate-migration:
	@read -p "Enter description: " description; \
	docker compose -f docker-compose.yml exec -T api alembic revision --autogenerate -m "$description"
