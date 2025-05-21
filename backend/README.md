# FastAPI Project - Backend

## Contents

- [Requirements](#requirements)
- [Docker Compose](#docker-compose)
- [General Workflow](#general-workflow)
- [VS Code](#vs-code)
- [Docker Compose Override](#docker-compose-override)
- [Backend tests](#backend-tests)
- [Migrations](#migrations)
- [Email Templates](#email-templates)
- [Analytics Module](#analytics-module)

## Requirements

* [Docker](https://www.docker.com/).
* [uv](https://docs.astral.sh/uv/) for Python package and environment management.

## Docker Compose

Start the local development environment with Docker Compose following the guide in [../development.md](../development.md).

## General Workflow

By default, the dependencies are managed with [uv](https://docs.astral.sh/uv/), go there and install it.

From `./backend/` you can install all the dependencies with:

```console
$ uv sync
```

Then you can activate the virtual environment with:

```console
$ source .venv/bin/activate
```

Make sure your editor is using the correct Python virtual environment, with the interpreter at `backend/.venv/bin/python`.

Modify or add SQLModel models for data and SQL tables in `./backend/app/models.py`, API endpoints in `./backend/app/api/`, CRUD (Create, Read, Update, Delete) utils in `./backend/app/crud.py`.

## VS Code

There are already configurations in place to run the backend through the VS Code debugger, so that you can use breakpoints, pause and explore variables, etc.

The setup is also already configured so you can run the tests through the VS Code Python tests tab.

## Docker Compose Override

During development, you can change Docker Compose settings that will only affect the local development environment in the file `docker-compose.override.yml`.

The changes to that file only affect the local development environment, not the production environment. So, you can add "temporary" changes that help the development workflow.

For example, the directory with the backend code is synchronized in the Docker container, copying the code you change live to the directory inside the container. That allows you to test your changes right away, without having to build the Docker image again. It should only be done during development, for production, you should build the Docker image with a recent version of the backend code. But during development, it allows you to iterate very fast.

There is also a command override that runs `fastapi run --reload` instead of the default `fastapi run`. It starts a single server process (instead of multiple, as would be for production) and reloads the process whenever the code changes. Have in mind that if you have a syntax error and save the Python file, it will break and exit, and the container will stop. After that, you can restart the container by fixing the error and running again:

```console
$ docker compose watch
```

There is also a commented out `command` override, you can uncomment it and comment the default one. It makes the backend container run a process that does "nothing", but keeps the container alive. That allows you to get inside your running container and execute commands inside, for example a Python interpreter to test installed dependencies, or start the development server that reloads when it detects changes.

To get inside the container with a `bash` session you can start the stack with:

```console
$ docker compose watch
```

and then in another terminal, `exec` inside the running container:

```console
$ docker compose exec backend bash
```

You should see an output like:

```console
root@7f2607af31c3:/app#
```

that means that you are in a `bash` session inside your container, as a `root` user, under the `/app` directory, this directory has another directory called "app" inside, that's where your code lives inside the container: `/app/app`.

There you can use the `fastapi run --reload` command to run the debug live reloading server.

```console
$ fastapi run --reload app/main.py
```

...it will look like:

```console
root@7f2607af31c3:/app# fastapi run --reload app/main.py
```

and then hit enter. That runs the live reloading server that auto reloads when it detects code changes.

Nevertheless, if it doesn't detect a change but a syntax error, it will just stop with an error. But as the container is still alive and you are in a Bash session, you can quickly restart it after fixing the error, running the same command ("up arrow" and "Enter").

...this previous detail is what makes it useful to have the container alive doing nothing and then, in a Bash session, make it run the live reload server.

## Backend tests

To test the backend run:

```console
$ bash ./scripts/test.sh
```

The tests run with Pytest, modify and add tests to `./backend/app/tests/`.

If you use GitHub Actions the tests will run automatically.

### Test running stack

If your stack is already up and you just want to run the tests, you can use:

```bash
docker compose exec backend bash scripts/tests-start.sh
```

That `/app/scripts/tests-start.sh` script just calls `pytest` after making sure that the rest of the stack is running. If you need to pass extra arguments to `pytest`, you can pass them to that command and they will be forwarded.

For example, to stop on first error:

```bash
docker compose exec backend bash scripts/tests-start.sh -x
```

### Test Coverage

When the tests are run, a file `htmlcov/index.html` is generated, you can open it in your browser to see the coverage of the tests.

## Migrations

As during local development your app directory is mounted as a volume inside the container, you can also run the migrations with `alembic` commands inside the container and the migration code will be in your app directory (instead of being only inside the container). So you can add it to your git repository.

Make sure you create a "revision" of your models and that you "upgrade" your database with that revision every time you change them. As this is what will update the tables in your database. Otherwise, your application will have errors.

* Start an interactive session in the backend container:

```console
$ docker compose exec backend bash
```

* Alembic is already configured to import your SQLModel models from `./backend/app/models.py`.

* After changing a model (for example, adding a column), inside the container, create a revision, e.g.:

```console
$ alembic revision --autogenerate -m "Add column last_name to User model"
```

* Commit to the git repository the files generated in the alembic directory.

* After creating the revision, run the migration in the database (this is what will actually change the database):

```console
$ alembic upgrade head
```

If you don't want to use migrations at all, uncomment the lines in the file at `./backend/app/core/db.py` that end in:

```python
SQLModel.metadata.create_all(engine)
```

and comment the line in the file `scripts/prestart.sh` that contains:

```console
$ alembic upgrade head
```

If you don't want to start with the default models and want to remove them / modify them, from the beginning, without having any previous revision, you can remove the revision files (`.py` Python files) under `./backend/app/alembic/versions/`. And then create a first migration as described above.

## Email Templates

The email templates are in `./backend/app/email-templates/`. Here, there are two directories: `build` and `src`. The `src` directory contains the source files that are used to build the final email templates. The `build` directory contains the final email templates that are used by the application.

Before continuing, ensure you have the [MJML extension](https://marketplace.visualstudio.com/items?itemName=attilabuti.vscode-mjml) installed in your VS Code.

Once you have the MJML extension installed, you can create a new email template in the `src` directory. After creating the new email template and with the `.mjml` file open in your editor, open the command palette with `Ctrl+Shift+P` and search for `MJML: Export to HTML`. This will convert the `.mjml` file to a `.html` file and now you can save it in the build directory.

## Analytics Module

This section details the integrated analytics capabilities, designed to provide insights into application data without impacting the performance of the primary transactional database.

### Architecture Overview

The analytics architecture employs a dual-database approach:

-   **PostgreSQL**: Serves as the primary transactional database, handling real-time data for Users, Items, and other core application entities.
-   **DuckDB with Polars**: Used as the analytical processing engine. Data is periodically moved from PostgreSQL to Parquet files, which are then queried efficiently by DuckDB. Polars is utilized for high-performance DataFrame manipulations where needed.

This separation ensures that complex analytical queries do not overload the operational database.

### ETL Process

An ETL (Extract, Transform, Load) process is responsible for populating the analytical data store.

-   **Script**: `backend/app/scripts/export_to_parquet.py`
-   **Purpose**: This script extracts data from the main PostgreSQL database (specifically the `User` and `Item` tables) and saves it into Parquet files (`users_analytics.parquet`, `items_analytics.parquet`). Parquet format is chosen for its efficiency in analytical workloads.
-   **Usage**: The script is designed to be run periodically (e.g., as a nightly batch job or via a scheduler like cron) to update the data available for analytics. To run the script manually (ensure your Python environment with backend dependencies is active, or run within the Docker container):
    ```bash
    python backend/app/scripts/export_to_parquet.py
    ```
-   **Output Location**: The Parquet files are stored in a directory specified by the `PARQUET_DATA_PATH` environment variable. The default location is `backend/data/parquet/`.

### Analytics API Endpoints

New API endpoints provide access to analytical insights. These are available under the `/api/v1/analytics` prefix:

-   **`GET /api/v1/analytics/items_by_user`**:
    -   **Provides**: A list of users and the total count of items they own.
    -   **Details**: Only includes users who own at least one item. Results are ordered by the number of items in descending order.
    -   **Response Model**: `List[UserItemCount]` where `UserItemCount` includes `email: str` and `item_count: int`.

-   **`GET /api/v1/analytics/active_users`**:
    -   **Provides**: The top 10 most active users, based on the number of items they own.
    -   **Details**: Users are ordered by item count in descending order. This endpoint uses a left join, so users who may not own any items could theoretically be included if the query were adjusted (currently, it effectively shows top item owners).
    -   **Response Model**: `List[ActiveUser]` where `ActiveUser` includes `user_id: int`, `email: str`, `full_name: str | None`, and `item_count: int`.

These endpoints query the DuckDB instance, which reads from the Parquet files generated by the ETL script.

### OpenTelemetry Tracing

OpenTelemetry has been integrated into the backend for enhanced observability:

-   **Purpose**: To trace application performance and behavior, helping to identify bottlenecks and understand request flows.
-   **Export**: Currently, traces are configured to be exported to the console. This is useful for development and debugging. For production, an appropriate OpenTelemetry collector and backend (e.g., Jaeger, Zipkin, Datadog) should be configured.
-   **Coverage**:
    -   **Auto-instrumentation**: FastAPI and SQLAlchemy interactions are automatically instrumented, providing traces for API requests and database calls to the PostgreSQL database.
    -   **Custom Tracing**:
        -   The analytics module (`backend/app/core/analytics.py`) includes custom spans for DuckDB connection setup and query execution.
        -   The analytics API routes (`backend/app/api/routes/analytics.py`) have custom spans for their request handlers.
        -   The ETL script (`backend/app/scripts/export_to_parquet.py`) is instrumented with custom spans for its key operations (database extraction, Parquet file writing).

### Key New Dependencies

The following main dependencies were added to support the analytics features:

-   `duckdb`: An in-process analytical data management system.
-   `polars`: A fast DataFrame library.
-   `opentelemetry-api`: Core OpenTelemetry API.
-   `opentelemetry-sdk`: OpenTelemetry SDK for configuring telemetry.
-   `opentelemetry-exporter-otlp-proto-http`: OTLP exporter (though console exporter is used by default in current setup).
-   `opentelemetry-instrumentation-fastapi`: Auto-instrumentation for FastAPI.
-   `opentelemetry-instrumentation-sqlalchemy`: Auto-instrumentation for SQLAlchemy.
-   `opentelemetry-instrumentation-psycopg2`: Auto-instrumentation for Psycopg2 (PostgreSQL driver).

Refer to `backend/pyproject.toml` for specific versions.

### New Configuration Options

The following environment variables can be set (e.g., in your `.env` file) to configure the analytics and OpenTelemetry features:

-   **`PARQUET_DATA_PATH`**:
    -   **Description**: Specifies the directory where the ETL script saves Parquet files and where DuckDB reads them from.
    -   **Default**: `backend/data/parquet/`
-   **`SERVICE_NAME`**:
    -   **Description**: Sets the service name attribute for OpenTelemetry traces. This helps in identifying and filtering traces in a distributed tracing system.
    -   **Default**: `fastapi-analytics-app` (Note: The ETL script appends "-etl-script" to this name for its traces).
-   **`OTEL_EXPORTER_OTLP_ENDPOINT`** (Optional, for future use):
    -   **Description**: If you configure an OTLP exporter (e.g., for Jaeger or Prometheus), this variable would specify its endpoint URL.
    -   **Default**: Not set (console exporter is used by default).

These settings are defined in `backend/app/core/config.py`.
