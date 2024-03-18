# Full Stack FastAPI Template

<a href="https://github.com/tiangolo/full-stack-fastapi-template/actions?query=workflow%3ATest" target="_blank"><img src="https://github.com/tiangolo/full-stack-fastapi-template/workflows/Test/badge.svg" alt="Test"></a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/tiangolo/full-stack-fastapi-template" target="_blank"><img src="https://coverage-badge.samuelcolvin.workers.dev/tiangolo/full-stack-fastapi-template.svg" alt="Coverage"></a>

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
    - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
    - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
    - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
- 🚀 [React](https://react.dev) for the frontend.
    - 💃 Using TypeScript, hooks, Vite, and other parts of a modern frontend stack.
    - 🎨 [Chakra UI](https://chakra-ui.com) for the frontend components.
    - 🤖 An automatically generated frontend client.
    - 🦇 Dark mode support.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT token authentication.
- 📫 Email based password recovery.
- ✅ Tests with [Pytest](https://pytest.org).
- 📞 [Traefik](https://traefik.io) as a reverse proxy / load balancer.
- 🚢 Deployment instructions using Docker Compose, including how to set up a frontend Traefik proxy to handle automatic HTTPS certificates.
- 🏭 CI (continuous integration) and CD (continuous deployment) based on GitHub Actions.

### Dashboard Login

[![API docs](img/login.png)](https://github.com/tiangolo/full-stack-fastapi-template)

### Dashboard - Admin

[![API docs](img/dashboard.png)](https://github.com/tiangolo/full-stack-fastapi-template)

### Dashboard - Create User

[![API docs](img/dashboard-create.png)](https://github.com/tiangolo/full-stack-fastapi-template)

### Dashboard - Items

[![API docs](img/dashboard-items.png)](https://github.com/tiangolo/full-stack-fastapi-template)

### Dashboard - User Settings

[![API docs](img/dashboard-user-settings.png)](https://github.com/tiangolo/full-stack-fastapi-template)

### Dashboard - Dark Mode

[![API docs](img/dashboard-dark.png)](https://github.com/tiangolo/full-stack-fastapi-template)

### Interactive API Documentation

[![API docs](img/docs.png)](https://github.com/tiangolo/full-stack-fastapi-template)

## How To Use It

You can **just fork or clone** this repository and use it as is.

✨ It just works. ✨

### Configure

You can then update configs in the `.env` files to customize your configurations.

Before deploying it, make sure you change at least the values for:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

### Generate Secret Keys

Some environment variables in the `.env` file have a default value of `changethis`.

You have to change them with a secret key, to generate secret keys you can run the following command:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the content and use that as password / secret key. And run that again to generate another secure key.

## How To Use It - Alternative With Copier

This repository also supports generating a new project using [Copier](https://copier.readthedocs.io).

It will copy all the files, ask you configuration questions, and update the `.env` files with your answers.

### Install Copier

You can install Copier with:

```bash
pip install copier
```

Or better, if you have [`pipx`](https://pipx.pypa.io/), you can run it with:

```bash
pipx install copier
```

**Note**: If you have `pipx`, installing copier is optional, you could run it directly.

### Generate a Project With Copier

Decide a name for your new project's directory, you will use it below. For example, `my-awesome-project`.

Go to the directory that will be the parent of your project, and run the command with your project's name:

```bash
copier copy https://github.com/tiangolo/full-stack-fastapi-template my-awesome-project --trust
```

If you have `pipx` and you didn't install `copier`, you can run it directly:

```bash
pipx run copier copy https://github.com/tiangolo/full-stack-fastapi-template my-awesome-project --trust
```

**Note** the `--trust` option is necessary to be able to execute a [post-creation script](https://github.com/tiangolo/full-stack-fastapi-template/blob/master/.copier/update_dotenv.py) that updates your `.env` files.

### Input Variables

Copier will ask you for some data, you might want to have at hand before generating the project.

But don't worry, you can just update any of that in the `.env` files afterwards.

The input variables, with their default values (some auto generated) are:

- `project_name`: (default: `"FastAPI Project"`) The name of the project, shown to API users (in .env).
- `stack_name`: (default: `"fastapi-project"`) The name of the stack used for Docker Compose labels (no spaces) (in .env).
- `secret_key`: (default: `"changethis"`) The secret key for the project, used for security, stored in .env, you can generate one with the method above.
- `first_superuser`: (default: `"admin@example.com"`) The email of the first superuser (in .env).
- `first_superuser_password`: (default: `"changethis"`) The password of the first superuser (in .env).
- `smtp_host`: (default: "") The SMTP server host to send emails, you can set it later in .env.
- `smtp_user`: (default: "") The SMTP server user to send emails, you can set it later in .env.
- `smtp_password`: (default: "") The SMTP server password to send emails, you can set it later in .env.
- `emails_from_email`: (default: `"info@example.com"`) The email account to send emails from, you can set it later in .env.
- `postgres_password`: (default: `"changethis"`) The password for the PostgreSQL database, stored in .env, you can generate one with the method above.
- `sentry_dsn`: (default: "") The DSN for Sentry, if you are using it, you can set it later in .env.

## Backend Development

Backend docs: [backend/README.md](./backend/README.md).

## Frontend Development

Frontend docs: [frontend/README.md](./frontend/README.md).

## Deployment

Deployment docs: [deployment.md](./deployment.md).

## Development

General development docs: [development.md](./development.md).

This includes using Docker Compose, custom local domains, `.env` configurations, etc.

## Release Notes

Check the file [release-notes.md](./release-notes.md).

## Contributors
Thanks goes to these wonderful contributors ([emoji key](https://allcontributors.org/docs/en/emoji-key) following [all-contributors](https://github.com/all-contributors/all-contributors) specification):

<table>
  <tbody>
    <tr>
      <td align="center"><a href="https://github.com/michaelfeil"><img src="https://avatars.githubusercontent.com/michaelfeil?v=4&s=100" width="100px;" alt="michaelfeil"/><br /><sub><b>michaelfeil</b></sub></a><br /><a href="https://github.com/amazon-science/chronos-forecasting/commits?author=michaelfeil" title="Code">💻</a> <a href="#doc-michaelfeil" title="Documentation">📖</a> <a href="#ideas-michaelfeil" title="Ideas, Planning, & Feedback">🤔</a> <a href="#review-michaelfeil" title="Reviewed Pull Requests">👀</a> <a href="#maintenance-michaelfeil" title="Maintenance">🚧</a> <a href="#infra-michaelfeil" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
      <td align="center"><a href="https://github.com/lostella"><img src="https://avatars.githubusercontent.com/lostella?v=4&s=100" width="100px;" alt="lostella"/><br /><sub><b>lostella</b></sub></a><br /><a href="#ideas-lostella" title="Ideas, Planning, & Feedback">🤔</a> <a href="#doc-lostella" title="Documentation">📖</a> <a href="#code-lostella" title="Code">💻</a> <a href="#design-lostella" title="Design">🎨</a> <a href="#research-lostella" title="Research">🔬</a></td>
      <td align="center" colspan="2"><a href="https://github.com/amazon-auto"><img src="https://avatars.githubusercontent.com/amazon-auto?v=4&s=100" width="100px;" alt="amazon-auto"/><br /><sub><b>amazon-auto</b></sub></a><br /><a href="#infra-amazon-auto" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#code-amazon-auto" title="Code">💻</a></td>
      <td align="center"><a href="https://github.com/abdulfatir"><img src="https://avatars.githubusercontent.com/abdulfatir?v=4&s=100" width="100px;" alt="abdulfatir"/><br /><sub><b>abdulfatir</b></sub></a><br /><a href="#code-abdulfatir" title="Code">💻</a></td>
      <td align="center"><a href="https://github.com/shchur"><img src="https://avatars.githubusercontent.com/shchur?v=4&s=100" width="100px;" alt="shchur"/><br /><sub><b>shchur</b></sub></a><br /><a href="#code-shchur" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" colspan="2"><a href="https://github.com/powerzbt"><img src="https://avatars.githubusercontent.com/powerzbt?v=4&s=100" width="100px;" alt="powerzbt"/><br /><sub><b>powerzbt</b></sub></a><br /><a href="#doc-powerzbt" title="Documentation">📖</a></td>
    </tr>
  </tbody>
</table>


## License

The Full Stack FastAPI Template is licensed under the terms of the MIT license.
