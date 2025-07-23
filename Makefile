check:
	cd backend && \
	uv run ruff check . --fix && \
	uv run ruff format .
