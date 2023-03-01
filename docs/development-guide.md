# Development and cookiecutter installation

1. [Getting started](getting-started.md)
2. [Development and installation](development-guide.md)
3. [Deployment for production](deployment-guide.md)
4. [Authentication and magic tokens](authentication-guide.md)

---

## Contents

- [Run Cookiecutter](#run-cookiecutter)
- [Generate passwords](#generate-passwords)
- [Input variables](#input-variables)
- [Local development](#local-development)
- [Starting Jupyter Lab](#starting-jupyter-lab)

## Run Cookiecutter

Go to the directory where you want to create your project and run:

```bash
pip install cookiecutter
cookiecutter https://github.com/whythawk/full-stack-fastapi-postgresql
```

## Generate passwords

You will be asked to provide passwords and secret keys for several components. Open another terminal and run:

```bash
openssl rand -hex 32
# Outputs something like: 99d3b1f01aa639e4a76f4fc281fc834747a543720ba4c8a8648ba755aef9be7f
```

Copy the contents and use that as password / secret key. And run that again to generate another secure key.

## Input variables

The generator (Cookiecutter) will ask you for data on a long list of fields which will be used to populate variables across the project, customising it for you out the box. You might want to have these on hand before generating the project.

The input variables, with their default values (some auto generated) are:

- `project_name`: The name of the project. This will also be the folder in which your project is generated.
- `project_slug`: The development friendly name of the project. By default, based on the project name
- `domain_main`: The domain in where to deploy the project for production (from the branch `production`), used by the load balancer, backend, etc. By default, based on the project slug.
- `domain_staging`: The domain in where to deploy while staging (before production) (from the branch `master`). By default, based on the main domain.
- `domain_base_api_url`: The domain url used by the frontend app for backend api calls. If deploying a localhost development environment, likely to be `http://localhost/api/v1`
- `domain_base_ws_url`: The domain url used by the frontend app for backend websocket calls. If deploying a localhost development environment, likely to be `ws://localhost/api/v1`
- `docker_swarm_stack_name_main`: The name of the stack while deploying to Docker in Swarm mode for production. By default, based on the domain.
- `docker_swarm_stack_name_staging`: The name of the stack while deploying to Docker in Swarm mode for staging. By default, based on the domain.
- `secret_key`: Backend server secret key. Use the method above to generate it.
- `first_superuser`: The first superuser generated, with it you will be able to create more users, etc. By default, based on the domain.
- `first_superuser_password`: First superuser password. Use the method above to generate it.
- `backend_cors_origins`: Origins (domains, more or less) that are enabled for CORS (Cross Origin Resource Sharing). This allows a frontend in one domain (e.g. `https://dashboard.example.com`) to communicate with this backend, that could be living in another domain (e.g. `https://api.example.com`). It can also be used to allow your local frontend (with a custom `hosts` domain mapping, as described in the project's `README.md`) that could be living in `http://dev.example.com:8080` to communicate with the backend at `https://stag.example.com`. Notice the `http` vs `https` and the `dev.` prefix for local development vs the "staging" `stag.` prefix. By default, it includes origins for production, staging and development, with ports commonly used during local development by several popular frontend frameworks (Vue with `:8080`, React, Angular).
- `smtp_port`: Port to use to send emails via SMTP. By default `587`.
- `smtp_host`: Host to use to send emails, it would be given by your email provider, like Mailgun, Sparkpost, etc.
- `smtp_user`: The user to use in the SMTP connection. The value will be given by your email provider.
- `smtp_password`: The password to be used in the SMTP connection. The value will be given by the email provider.
- `smtp_emails_from_email`: The email account to use as the sender in the notification emails, it could be something like `info@your-custom-domain.com`.
- `smtp_emails_from_name`: The email account name to use as the sender in the notification emails, it could be something like `Symona Adaro`.
- `smtp_emails_to_email`: The email account to use as the recipient for `contact us` emails, it could be something like `requests@your-custom-domain.com`.
- `postgres_password`: Postgres database password. Use the method above to generate it. (You could easily modify it to use MySQL, MariaDB, etc).
- `pgadmin_default_user`: PGAdmin default user, to log-in to the PGAdmin interface.
- `pgadmin_default_user_password`: PGAdmin default user password. Generate it with the method above.
- `neo4j_password`: Neo4j database password. Use the method above to generate it.
- `traefik_constraint_tag`: The tag to be used by the internal Traefik load balancer (for example, to divide requests between backend and frontend) for production. Used to separate this stack from any other stack you might have. This should identify each stack in each environment (production, staging, etc).
- `traefik_constraint_tag_staging`: The Traefik tag to be used while on staging.
- `traefik_public_constraint_tag`: The tag that should be used by stack services that should communicate with the public.
- `flower_auth`: Basic HTTP authentication for flower, in the form`user:password`. By default: "`admin:changethis`".
- `sentry_dsn`: Key URL (DSN) of Sentry, for live error reporting. You can use the open source version or a free account. E.g.: `https://1234abcd:5678ef@sentry.example.com/30`.
- `docker_image_prefix`: Prefix to use for Docker image names. If you are using GitLab Docker registry it would be based on your code repository. E.g.: `git.example.com/development-team/my-awesome-project/`.
- `docker_image_backend`: Docker image name for the backend. By default, it will be based on your Docker image prefix, e.g.: `git.example.com/development-team/my-awesome-project/backend`. And depending on your environment, a different tag will be appended ( `prod`, `stag`, `branch` ). So, the final image names used will be like: `git.example.com/development-team/my-awesome-project/backend:prod`.
- `docker_image_celeryworker`: Docker image for the celery worker. By default, based on your Docker image prefix.
- `docker_image_frontend`: Docker image for the frontend. By default, based on your Docker image prefix.

## Local development

Once the Cookiecutter script has completed, you will have a folder populated with the base project and all input variables customised. 

Change into the project folder and run the `docker-compose` script to build the project containers:

```bash
docker-compose build --no-cache
```

And start them:

```bash
docker-compose up -d 
```

**NOTE:** The Nuxt image does not automatically refresh while running in development mode. Any changes will need a rebuild. This gets tired fast, so it's easier to run Nuxt outside Docker and call through to the `backend` for API calls. You can then view the frontend at `http://localhost:3000` and the backend api endpoints at `http://localhost/redoc`. This problem won't be a concern in production.

Change into the `/frontend` folder, and:

```bash
yarn install
yarn dev
```

Be careful about the version of `Node.js` you're using. As of today (December 2022), the latest Node version supported by Nuxt is 16.18.1.

FastAPI `backend` updates will refresh automatically, but the `celeryworker` container must be restarted before changes take effect.

## Starting Jupyter Lab

If you like to do algorithmic development and testing in Jupyter Notebooks, then launch the `backend` terminal and start Jupyter as follows:

```bash
docker-compose exec backend bash
```

From the terminal:

```bash
$JUPYTER
```

Copy the link generated into your browser and start.

**NOTE:** Notebooks developed in the container are not saved outside, so remember to copy them for persistence. You can do that from inside Jupyter (download), or:

```bash
docker cp <containerId>:/file/path/within/container /host/path/target
```

Or share a folder via `docker-compose.override.yml`.

At this point, development is over to you.
