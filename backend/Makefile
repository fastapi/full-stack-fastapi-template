export ENVIRONMENT=local

test:
	docker compose down -v --remove-orphans; \
	op run --no-masking --env-file="../.env" -- docker compose up -d db mailcatcher; \
	op run --no-masking --env-file="../.env" -- uv run bash scripts/prestart.sh; \
	op run --no-masking --env-file="../.env" -- uv run bash scripts/tests-start.sh $(MSG); \
	docker compose down -v --remove-orphans;

lint:
	uv run bash scripts/lint.sh

format:
	uv run bash scripts/format.sh

.PHONY: test lint format
