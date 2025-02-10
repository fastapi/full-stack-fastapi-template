export ENVIRONMENT=local


watch:
	op run --env-file=".env" -- docker compose watch

up:
	op run --env-file=".env" -- docker compose up

build:
	op run --env-file=".env" -- docker compose build

.PHONY: watch up build