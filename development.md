# FastAPI Project - Development

## Development in `localhost` with a custom domain

You might want to use something different than `localhost` as the domain. For example, if you are having problems with cookies that need a subdomain, and Chrome is not allowing you to use `localhost`.

In that case, you have two options: you could use the instructions to modify your system `hosts` file with the instructions below in **Development with a custom IP** or you can just use `localhost.tiangolo.com`, it is set up to point to `localhost` (to the IP `127.0.0.1`) and all its subdomains too. And as it is an actual domain, the browsers will store the cookies you set during development, etc.

If you used the default CORS enabled domains while generating the project, `localhost.tiangolo.com` was configured to be allowed. If you didn't, you will need to add it to the list in the variable `BACKEND_CORS_ORIGINS` in the `.env` file.

To configure it in your stack, follow the section **Change the development "domain"** below, using the domain `localhost.tiangolo.com`.

After performing those steps you should be able to open: http://localhost.tiangolo.com and it will be served by your stack in `localhost`.

Check all the corresponding available URLs in the section at the end.

## Development with a custom IP

If you are running Docker in an IP address different than `127.0.0.1` (`localhost`), you will need to perform some additional steps. That will be the case if you are running a custom Virtual Machine or your Docker is located in a different machine in your network.

In that case, you will need to use a fake local domain (`dev.example.com`) and make your computer think that the domain is served by the custom IP (e.g. `192.168.99.150`).

If you have a custom domain like that, you need to add it to the list in the variable `BACKEND_CORS_ORIGINS` in the `.env` file.

* Open your `hosts` file with administrative privileges using a text editor:

  * **Note for Windows**: If you are in Windows, open the main Windows menu, search for "notepad", right click on it, and select the option "open as Administrator" or similar. Then click the "File" menu, "Open file", go to the directory `c:\Windows\System32\Drivers\etc\`, select the option to show "All files" instead of only "Text (.txt) files", and open the `hosts` file.
  * **Note for Mac and Linux**: Your `hosts` file is probably located at `/etc/hosts`, you can edit it in a terminal running `sudo nano /etc/hosts`.

* Additional to the contents it might have, add a new line with the custom IP (e.g. `192.168.99.150`) a space character, and your fake local domain: `dev.example.com`.

The new line might look like:

```
192.168.99.150    dev.example.com
```

* Save the file.
  * **Note for Windows**: Make sure you save the file as "All files", without an extension of `.txt`. By default, Windows tries to add the extension. Make sure the file is saved as is, without extension.

...that will make your computer think that the fake local domain is served by that custom IP, and when you open that URL in your browser, it will talk directly to your locally running server when it is asked to go to `dev.example.com` and think that it is a remote server while it is actually running in your computer.

To configure it in your stack, follow the section **Change the development "domain"** below, using the domain `dev.example.com`.

After performing those steps you should be able to open: http://dev.example.com and it will be server by your stack in `192.168.99.150`.

Check all the corresponding available URLs in the section at the end.

## Change the development "domain"

If you need to use your local stack with a different domain than `localhost`, you need to make sure the domain you use points to the IP where your stack is set up.

To simplify your Docker Compose setup, for example, so that the API docs (Swagger UI) knows where is your API, you should let it know you are using that domain for development.

* Open the file located at `./.env`. It would have a line like:

```
DOMAIN=localhost
```

* Change it to the domain you are going to use, e.g.:

```
DOMAIN=localhost.tiangolo.com
```

That variable will be used by the Docker Compose files.

After that, you can restart your stack with:

```bash
docker compose up -d
```

and check all the corresponding available URLs in the section at the end.

## Docker Compose files and env vars

There is a main `docker-compose.yml` file with all the configurations that apply to the whole stack, it is used automatically by `docker compose`.

And there's also a `docker-compose.override.yml` with overrides for development, for example to mount the source code as a volume. It is used automatically by `docker compose` to apply overrides on top of `docker-compose.yml`.

These Docker Compose files use the `.env` file containing configurations to be injected as environment variables in the containers.

They also use some additional configurations taken from environment variables set in the scripts before calling the `docker compose` command.

## The .env file

The `.env` file is the one that contains all your configurations, generated keys and passwords, etc.

Depending on your workflow, you could want to exclude it from Git, for example if your project is public. In that case, you would have to make sure to set up a way for your CI tools to obtain it while building or deploying your project.

One way to do it could be to add each environment variable to your CI/CD system, and updating the `docker-compose.yml` file to read that specific env var instead of reading the `.env` file.

### Pre-commits and code linting

we are using a tool called pre-commit for code linting https://pre-commit.com/.

Summary taken from oficial website

Git hook scripts are useful for identifying simple issues before submission to code review. We run our hooks on every commit to automatically point out issues in code such as missing semicolons, trailing whitespace, and debug statements. By pointing these issues out before code review, this allows a code reviewer to focus on the architecture of a change while not wasting time with trivial style nitpicks.

You can find `.pre-commit-config.yaml` at the root of the project, where you can see somethink like this.

```yaml
# See https://pre-commit.com for more information
# See https://pre-commit.com/hooks.html for more hooks
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: check-added-large-files
      - id: check-toml
      - id: check-yaml
        args:
          - --unsafe
      - id: end-of-file-fixer
      - id: trailing-whitespace
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.2.2
    hooks:
      - id: ruff
        args:
          - --fix
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.53.0
    hooks:
      - id: eslint
        files: \.[jt]sx?$
        types: [file]
        additional_dependencies:
          - eslint@8.53.0
          - eslint-plugin-react-hooks@4.6.0
          - eslint-plugin-react-refresh@0.4.4
          - "@typescript-eslint/eslint-plugin@6.10.0"
          - "@typescript-eslint/parser@6.10.0"
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        files: \.(ts|tsx)$
        additional_dependencies:
          - prettier@3.2.5

ci:
  autofix_commit_msg: 🎨 [pre-commit.ci] Auto format from pre-commit.com hooks
  autoupdate_commit_msg: ⬆ [pre-commit.ci] pre-commit autoupdate
```

As you can see we have some hooks that could be familiar for you, like ruff to format python code and eslint/prettier for the front end stuff.

#### Running pre-commit hooks automatically

There is a way to install the hooks, in this way whenever yo do a commit the hooks will be trigger to ensure everything it's ok.

To install the pre-commit hooks it's as simple as run this command

```bash
❯ poetry run pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

Let's suppose we have a python file with some imports unordered like this

```python
from collections.abc import Generator

import pytest
from sqlmodel import Session, delete
from fastapi.testclient import TestClient # <<- this file isn't ordered

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import Item, User
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers
```

So we have this error

Import block is un-sorted or un-formatted Ruff

Despite the code it's ok and will be executed without errors, it is not formatted.

```bash
❯ git status
On branch develop
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   app/tests/conftest.py
```

now I'm going to commit mi changes as usual

```bash
full-stack-fastapi-postgresql/backend on  develop
❯ git add app/tests/conftest.py

full-stack-fastapi-postgresql/backend on  develop
❯ git commit -m "Test pre commits hooks"
[WARNING] Unstaged files detected.
[INFO] Stashing unstaged files to /home/esteban/.cache/pre-commit/patch1710376375-647837.
[INFO] Initializing environment for https://github.com/charliermarsh/ruff-pre-commit.
[INFO] Initializing environment for https://github.com/pre-commit/mirrors-eslint.
[INFO] Initializing environment for https://github.com/pre-commit/mirrors-eslint:eslint@8.53.0,eslint-plugin-react-hooks@4.6.0,eslint-plugin-react-refresh@0.4.4,@typescript-eslint/eslint-plugin@6.10.0,@typescript-eslint/parser@6.10.0.
[INFO] Initializing environment for https://github.com/pre-commit/mirrors-prettier.
[INFO] Initializing environment for https://github.com/pre-commit/mirrors-prettier:prettier@3.2.5.
[INFO] Installing environment for https://github.com/pre-commit/pre-commit-hooks.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
[INFO] Installing environment for https://github.com/charliermarsh/ruff-pre-commit.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
[INFO] Installing environment for https://github.com/pre-commit/mirrors-eslint.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
[INFO] Installing environment for https://github.com/pre-commit/mirrors-prettier.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
check for added large files..............................................Passed
check toml...........................................(no files to check)Skipped
check yaml...........................................(no files to check)Skipped
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
ruff.....................................................................Failed
- hook id: ruff
- files were modified by this hook

Found 1 error (1 fixed, 0 remaining).

ruff-format..............................................................Passed
eslint...............................................(no files to check)Skipped
prettier.............................................(no files to check)Skipped
[INFO] Restored changes from /home/esteban/.cache/pre-commit/patch1710376375-647837.
```

After I made the commit, the first time you are going to see the messages initializing enviroment and installing, after everything is installed the next time is gonna run faster.

As you can see we got an error with ruff, and ruff applied the formatting. SInce there was an error in the linters it happens the next steps.

1. First, ruff detected unformatted code and then fix it.

2. Your commit isn't save, because the pre-commit hooks fail.

3. Since ruff made changes to fix your code is in stage again and you have to add it and commit it as usual, this time will be save since all the hooks are gonna pass

```bash
❯ git status
On branch develop
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   app/tests/conftest.py

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   app/tests/conftest.py
```

```bash
full-stack-fastapi-postgresql/backend on  develop
❯ git add app/tests/conftest.py

full-stack-fastapi-postgresql/backend on  develop
❯ git commit -m "Test pre commits hooks"
[WARNING] Unstaged files detected.
[INFO] Stashing unstaged files to /home/esteban/.cache/pre-commit/patch1710376851-661240.
check for added large files..............................................Passed
check toml...........................................(no files to check)Skipped
check yaml...........................................(no files to check)Skipped
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
eslint...............................................(no files to check)Skipped
prettier.............................................(no files to check)Skipped
[INFO] Restored changes from /home/esteban/.cache/pre-commit/patch1710376851-661240.
[develop 7eb8d8f] Test pre commits hooks
 1 file changed, 9 deletions(-)
```

Yay, everything just passed and our commit was saved!

#### Running pre-commit hooks manually

you can also run the pre-commits manually if you want and avoid the hook installation

```bash
❯ poetry run pre-commit run --all-files
check for added large files..............................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
eslint...................................................................Passed
prettier.................................................................Passed
```

## URLs

The production or staging URLs would use these same paths, but with your own domain.

### Development URLs

Development URLs, for local development.

Frontend: http://localhost

Backend: http://localhost/api/

Automatic Interactive Docs (Swagger UI): https://localhost/docs

Automatic Alternative Docs (ReDoc): https://localhost/redoc

Adminer: http://localhost:8080

Traefik UI: http://localhost:8090

### Development in localhost with a custom domain URLs

Development URLs, for local development.

Frontend: http://localhost.tiangolo.com

Backend: http://localhost.tiangolo.com/api/

Automatic Interactive Docs (Swagger UI): https://localhost.tiangolo.com/docs

Automatic Alternative Docs (ReDoc): https://localhost.tiangolo.com/redoc

Adminer: http://localhost.tiangolo.com:8080

Traefik UI: http://localhost.tiangolo.com:8090
