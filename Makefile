check:
	cd backend && \
	uv run ruff check . --fix && \
	uv run ruff format .


run-docker:
	docker compose up --build
