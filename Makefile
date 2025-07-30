check:
	cd backend && \
	uv run ruff check . --fix && \
	uv run ruff format .


run-docker:
	docker compose up --build


upload:
	rsync -avz backend/dataset/ \
	boetus-dg@173.199.118.92:/home/boetus-dg/htdocs/dg.boetus.com/dockge-stacks/analytics-app/backend/dataset
