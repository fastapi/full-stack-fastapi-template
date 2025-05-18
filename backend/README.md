# FastAPI Project - Backend

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

## Modular Monolith Architecture

This project follows a modular monolith architecture, which organizes the codebase into domain-specific modules while maintaining the deployment simplicity of a monolith.

### Module Structure

Each module follows this structure:

```
app/modules/{module_name}/
├── __init__.py           # Module initialization
├── api/                  # API layer
│   ├── __init__.py
│   ├── dependencies.py   # Module-specific dependencies
│   └── routes.py         # API endpoints
├── domain/               # Domain layer
│   ├── __init__.py
│   ├── events.py         # Domain events
│   └── models.py         # Domain models
├── repository/           # Data access layer
│   ├── __init__.py
│   └── {module}_repo.py  # Repository implementation
└── services/             # Business logic layer
    ├── __init__.py
    └── {module}_service.py  # Service implementation
```

### Available Modules

- **Auth**: Authentication and authorization
- **Users**: User management
- **Items**: Item management
- **Email**: Email sending and templates

### Working with Modules

To add functionality to an existing module, locate the appropriate layer (API, domain, repository, or service) and make your changes there.

To create a new module, follow the structure above and register it in `app/api/main.py`.

For more details, see the [Modular Monolith Implementation](./MODULAR_MONOLITH_IMPLEMENTATION.md) document.

### Adding New Features

When adding new features to the application:

- Add SQLModel models in the appropriate module's `domain/models.py` file
- Add API endpoints in the module's `api/routes.py` file
- Implement business logic in the module's `services/` directory
- Create repositories for data access in the module's `repository/` directory
- Define domain events in the module's `domain/events.py` file when needed

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

* Alembic is configured to import models from their respective modules in the modular architecture

* After changing a model (for example, adding a column), inside the container, create a revision, e.g.:

```console
$ alembic revision --autogenerate -m "Add column last_name to User model"
```

* For more details on working with Alembic in the modular architecture, see the [Modular Monolith Implementation](./MODULAR_MONOLITH_IMPLEMENTATION.md#alembic-migration-environment) document.

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

## Event System

The project includes an event system for communication between modules. This allows for loose coupling while maintaining clear communication paths.

### Publishing Events

To publish an event from a module:

1. Define an event class in the module's `domain/events.py` file:

```python
from app.core.events import EventBase

class MyEvent(EventBase):
    event_type: str = "my.event"
    # Add event properties here

    def publish(self) -> None:
        from app.core.events import publish_event
        publish_event(self)
```

2. Publish the event from a service:

```python
event = MyEvent(property1="value1", property2="value2")
event.publish()
```

### Subscribing to Events

To subscribe to events:

1. Create an event handler in a module's services directory:

```python
from app.core.events import event_handler
from other_module.domain.events import OtherEvent

@event_handler("other.event")
def handle_other_event(event: OtherEvent) -> None:
    # Handle the event
    pass
```

2. Import the handler in the module's `__init__.py` to register it.

For more details, see the [Event System Documentation](./MODULAR_MONOLITH_IMPLEMENTATION.md#event-system-implementation).

## Email Templates

The email templates are in `./backend/app/email-templates/`. Here, there are two directories: `build` and `src`. The `src` directory contains the source files that are used to build the final email templates. The `build` directory contains the final email templates that are used by the application.

Before continuing, ensure you have the [MJML extension](https://marketplace.visualstudio.com/items?itemName=attilabuti.vscode-mjml) installed in your VS Code.

Once you have the MJML extension installed, you can create a new email template in the `src` directory. After creating the new email template and with the `.mjml` file open in your editor, open the command palette with `Ctrl+Shift+P` and search for `MJML: Export to HTML`. This will convert the `.mjml` file to a `.html` file and now you can save it in the build directory.
