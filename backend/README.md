# FastAPI Project - Backend

## Requirements

* [Docker](https://www.docker.com/).
* [uv](https://docs.astral.sh/uv/) for Python package and environment management.

## Docker Compose

Start the local development environment with Docker Compose following the guide in [../development.md](../development.md).

## General Workflow

Dependencies are managed with [uv](https://docs.astral.sh/uv/). If you haven't already, please install it.

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

VS Code configurations are provided to run the backend with the debugger, allowing use of breakpoints, variable exploration, etc.

The setup also allows running tests via the VS Code Python tests tab.

## Docker Compose Override

Docker Compose settings specific to local development can be configured in `docker-compose.override.yml`.

These overrides only affect the local development environment, not production, allowing for temporary changes that aid development.

For instance, the backend code directory is synchronized with the Docker container, reflecting live code changes inside the container. This allows for immediate testing of changes without rebuilding the Docker image. This live synchronization is intended for development; for production, Docker images should be built with the finalized code. This approach significantly speeds up the development iteration cycle.

There is also a command override that runs `fastapi dev` instead of the default command. It starts a single server process (unlike multiple processes typical for production) and reloads the process whenever code changes are detected. Note that a syntax error in a saved Python file will cause the server to break and exit, stopping the container. After fixing the error, the container can be restarted by running:

```console
$ docker compose watch
```

A commented-out `command` override is available in `docker-compose.override.yml`. If uncommented (and the default one commented out), it makes the backend container run a minimal process that keeps it alive without starting the main application. This allows you to `exec` into the running container and execute commands manually, such as starting a Python interpreter, testing installed dependencies, or running the development server with live reload.

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

There you can use the `fastapi dev` command to run the debug live reloading server.

```console
$ fastapi dev app/main.py
```

...it will look like:

```console
root@7f2607af31c3:/app# fastapi dev app/main.py
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

During local development, the application directory is mounted as a volume within the container. This allows you to run Alembic migration commands inside the container, with the generated migration code appearing directly in your application directory, ready to be committed to Git.

Make sure you create a "revision" of your models and that you "upgrade" your database with that revision every time you change them. As this is what will update the tables in your database. Otherwise, your application will have errors.

* Start an interactive session in the backend container:

```console
$ docker compose exec backend bash
```

* Alembic is configured to import SQLModel models from `./backend/app/models.py`.

* After changing a model (for example, adding a column), inside the container, create a revision, e.g.:

```console
$ alembic revision --autogenerate -m "Add column last_name to User model"
```

* Commit to the git repository the files generated in the alembic directory.

* After creating the revision, run the migration in the database (this is what will actually change the database):

```console
$ alembic upgrade head
```

If migrations are not desired for this project, uncomment the lines in `./backend/app/core/db.py` that end with:

```python
SQLModel.metadata.create_all(engine)
```

and comment the line in the file `scripts/prestart.sh` that contains:

```console
$ alembic upgrade head
```

If you need to reset or start fresh with migrations (e.g., squash existing migrations or initialize a new migration history), you can remove the existing revision files (the `.py` Python files) under `./backend/app/alembic/versions/`. After doing so, you can create a new initial migration as described above.

## Email Templates

The email templates are in `./backend/app/email-templates/`. Here, there are two directories: `build` and `src`. The `src` directory contains the source files that are used to build the final email templates. The `build` directory contains the final email templates that are used by the application.

Before continuing, ensure you have the [MJML extension](https://marketplace.visualstudio.com/items?itemName=attilabuti.vscode-mjml) installed in your VS Code.

Once you have the MJML extension installed, you can create a new email template in the `src` directory. After creating the new email template and with the `.mjml` file open in your editor, open the command palette with `Ctrl+Shift+P` and search for `MJML: Export to HTML`. This will convert the `.mjml` file to a `.html` file and now you can save it in the build directory.
