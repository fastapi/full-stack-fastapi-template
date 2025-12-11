# FastAPI Project - Backend Async

## Requirements

* [Docker](https://www.docker.com/).
* [uv](https://docs.astral.sh/uv/) for Python package and environment management.

## Quick Start

By default, the dependencies are managed with [uv](https://docs.astral.sh/uv/), go there and install it.

From `./backend_async/` you can install all the dependencies with:

```console
$ uv sync
```

Then you can activate the virtual environment with:

```console
$ source .venv/bin/activate
```

Make sure your editor is using the correct Python virtual environment, with the interpreter at `backend_async/.venv/bin/python`.

Start database containers and migrate:

```console
$ docker compose up -d db
$ alembic upgrade head
```

Start development server:

```console
$ fastapi dev
```

Modify or add SQLModel models for data and SQL tables in `./backend_async/app/models.py`, API endpoints in `./backend_async/app/api/`, CRUD (Create, Read, Update, Delete) utils in `./backend_async/app/crud.py`.

## Tests

Async tests are run using anyio backend. Here we also demonstrate setup using a separate test database, so ensure that the database container is up and running (see Quick Start).

From `./backend_async/` you can run:

```console
$ pytest
```

For coverage:

```console
$ coverage run -m pytest
```

To view coverage report:

```console
$ coverage report -m
```
