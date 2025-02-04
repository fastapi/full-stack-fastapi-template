# FastAPI Project - Backend

## Requirements

* [Docker](https://www.docker.com/).
* [Poetry](https://python-poetry.org/) for Python package and environment management.

## Local Development

* Start the stack with Docker Compose:

```bash
docker compose up -d
```

* Now you can open your browser and interact with these URLs:

Frontend, built with Docker, with routes handled based on the path: http://localhost

Automatic interactive documentation with Swagger UI (from the OpenAPI backend): http://localhost/docs

Adminer, database web administration: http://localhost:8080

Traefik UI, to see how the routes are being handled by the proxy: http://localhost:8090

**Note**: The first time you start your stack, it might take a minute for it to be ready. While the backend waits for the database to be ready and configures everything. You can check the logs to monitor it.

To check the logs, run:

```bash
docker compose logs
```

To check the logs of a specific service, add the name of the service, e.g.:

```bash
docker compose logs backend
```

If your Docker is not running in `localhost` (the URLs above wouldn't work) you would need to use the IP or domain where your Docker is running.

## Backend local development, additional details

### General workflow

By default, the dependencies are managed with [Poetry](https://python-poetry.org/), go there and install it.

From `./backend/` you can install all the dependencies with:

```console
$ poetry install
```

Then you can start a shell session with the new environment with:

```console
$ poetry shell
```

Make sure your editor is using the correct Python virtual environment.

Modify or add SQLModel models for data and SQL tables in `./backend/app/models.py`, API endpoints in `./backend/app/api/`, CRUD (Create, Read, Update, Delete) utils in `./backend/app/crud.py`.

### VS Code

There are already configurations in place to run the backend through the VS Code debugger, so that you can use breakpoints, pause and explore variables, etc.

The setup is also already configured so you can run the tests through the VS Code Python tests tab.

### Docker Compose Override

During development, you can change Docker Compose settings that will only affect the local development environment in the file `docker-compose.override.yml`.

The changes to that file only affect the local development environment, not the production environment. So, you can add "temporary" changes that help the development workflow.

For example, the directory with the backend code is mounted as a Docker "host volume", mapping the code you change live to the directory inside the container. That allows you to test your changes right away, without having to build the Docker image again. It should only be done during development, for production, you should build the Docker image with a recent version of the backend code. But during development, it allows you to iterate very fast.

There is also a command override that runs `/start-reload.sh` (included in the base image) instead of the default `/start.sh` (also included in the base image). It starts a single server process (instead of multiple, as would be for production) and reloads the process whenever the code changes. Have in mind that if you have a syntax error and save the Python file, it will break and exit, and the container will stop. After that, you can restart the container by fixing the error and running again:

```console
$ docker compose up -d
```

There is also a commented out `command` override, you can uncomment it and comment the default one. It makes the backend container run a process that does "nothing", but keeps the container alive. That allows you to get inside your running container and execute commands inside, for example a Python interpreter to test installed dependencies, or start the development server that reloads when it detects changes.

To get inside the container with a `bash` session you can start the stack with:

```console
$ docker compose up -d
```

and then `exec` inside the running container:

```console
$ docker compose exec backend bash
```

that means that you are in a `bash` session inside your container, as a `root` user, under the `/app` directory, this directory has another directory called "app" inside, that's where your code lives inside the container: `/app/app`.

### Migrations

Make sure you create a "revision" of your models and upgrade your database with that revision every time you change them. This updates your database schema to reflect model changes and prevents application errors.

#### Steps to Perform Migration

1. **Start an Interactive Session:**  
   Open a shell inside the backend container:
   ```bash
   docker compose exec backend bash
   ```

2. **Generate a New Migration Revision:**  
   Automatically create a new migration based on your model changes:
   ```bash
   alembic revision --autogenerate -m "Describe your schema changes"
   ```

3. **Review the Migration Script:**  
   Check the generated migration file in the migrations directory to confirm the changes. Modify the migration file if necessary.

4. **Apply the Migration:**  
   Run the migration to update your database schema:
   ```bash
   alembic upgrade head
   ```

5. **Verify the Update:**  
   Ensure that your database reflects the changes by reviewing logs or using a database client.

* Start an interactive session in the backend container:

## Additional Backend Documentation

### Project Structure

- **app/**
  - **api/**: Contains the RESTful API endpoint definitions using FastAPI. Each module here relates to a specific resource by:
    - Defining route paths for HTTP methods (GET, POST, PUT, DELETE).
    - Validating input data using Pydantic models.
    - Handling exceptions and returning standardized JSON responses compliant with OpenAPI.
  - **models.py**: Contains the SQLModel-based database models that define:
    - The table schema including columns, data types, and constraints.
    - Relationships between tables along with validation rules and default values.
    **Note:** Always generate a new Alembic migration and upgrade your database after modifying this file.
  - **crud.py**: Implements a set of CRUD functions that abstract database interactions, including:
    - Creating and inserting new records.
    - Fetching single or multiple records.
    - Updating records with new data.
    - Deleting records with robust error handling.
- **Docker Setup**
  - `docker-compose.yml` & `docker-compose.override.yml`: Used to start the entire stack for development. The volume mappings allow live reloading of code changes.
  - `.dockerignore`: Lists files and directories that are not needed during the Docker build process.
- **Version Control**
  - `.gitignore`: Ensures that generated files (like caches, virtual environments, etc.) are not committed to version control.

### Development Workflow

- **Dependency management:** Uses [Poetry](https://python-poetry.org/) to handle dependencies and virtual environments.
- **Running the application:** Start the services with:
  ```bash
  docker compose up -d
  ```
  Then, for local development and debugging, you can attach to the backend container using:
  ```bash
  docker compose exec backend bash
  ```
- **Migrations:** Use Alembic for database schema migrations. Always update your migration scripts when modifying models.
- **Debugging & Testing:** Leverage the VS Code configurations to set breakpoints and run tests directly from the editor.

### Extending the Application

- **Adding New APIs:** When creating new endpoints, add a new module under the `app/api/` directory. Each endpoint should:
    - Define RESTful routes implementing the required CRUD functionalities.
    - Use dependency injection to handle authentication and request validation.
    - Return structured responses according to OpenAPI standards.
- **Modifying Data Models:** When altering `app/models.py`:
    - Update table schemas, add or modify columns, and adjust relationships.
    - Create and apply a corresponding Alembic migration to keep the database schema synchronized.

This section is intended to serve as a high-level guide for both new and experienced developers on understanding and extending the backend of this FastAPI project.

## Modules Overview

### Schema

The `app/schema/` directory contains Pydantic models that are responsible for:
 - **Data Structure Definition:** Outlining the data formats used for API requests and responses.
 - **Validation & Serialization:** Enforcing business logic and ensuring that incoming and outgoing data adhere to expected formats. For example, custom validators (such as in `carousel_poster.py`) ensure that specific business rules are followed.
 - **ORM Integration:** Converting ORM objects into serializable formats using the `from_attributes = True` configuration.

### Core

The `app/core/` directory includes essential modules that form the backbone of the application:
 - **config.py:** Manages application configuration and environment variables using Pydantic's BaseSettings. It also constructs derived settings (like the SQLAlchemy database URI and server host).
 - **db.py:** Initializes and provides access to the database engine and sessions, ensuring smooth database connectivity and supporting operations like database initialization.
 - **security.py:** Implements security measures such as JWT-based token creation and validation, ensuring secure API operations.

These modules together ensure a modular, secure, and maintainable backend system.