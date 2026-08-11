# FastAPI Project - Deployment

Deploy the project to [FastAPI Cloud](https://fastapicloud.com) with the included GitHub Actions workflow.

## Create the FastAPI Cloud Application

Create an application in FastAPI Cloud and set its [Application Directory](https://fastapicloud.com/docs/builds-and-deployments/application-directory/) to `backend`.

Connect a PostgreSQL database using the [Neon](https://fastapicloud.com/docs/integrations/neon-integration/) or [Supabase](https://fastapicloud.com/docs/integrations/supabase-integration/) integration. Both integrations configure a `DATABASE_URL` secret automatically. You can also configure `DATABASE_URL` manually for another PostgreSQL provider.

## Configure the Application

### Environment Variables

Add these required [environment variables](https://fastapicloud.com/docs/builds-and-deployments/environment-variables/) to the FastAPI Cloud application:

* `PROJECT_NAME`: The name of the project, used in the API documentation and emails.
* `FIRST_SUPERUSER`: The email address of the first superuser.
* `FRONTEND_HOST`: The public URL of the application, such as the generated `https://your-app.fastapicloud.dev` URL or a custom domain.

To enable emails, add these optional environment variables with values from your email provider:

* `SMTP_HOST`
* `SMTP_USER`
* `EMAILS_FROM_EMAIL`

To enable Sentry, configure `SENTRY_DSN`.

### Secrets

Add these required values and mark them as secrets:

* `SECRET_KEY`: A secret key used to sign security tokens.
* `FIRST_SUPERUSER_PASSWORD`: The password of the first superuser.
* `DATABASE_URL`: The PostgreSQL connection URL, configured automatically when using a database integration.

To enable emails with an authenticated provider, add `SMTP_PASSWORD` as a secret.

You can generate secure values for `SECRET_KEY` and `FIRST_SUPERUSER_PASSWORD` with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Configure Continuous Deployment

The included `.github/workflows/deploy.yml` workflow builds the frontend, prepares the database, and deploys the application whenever changes are pushed to `master`. You can also run it manually from the **Actions** tab.

Log in to FastAPI Cloud and configure the [deploy token](https://fastapicloud.com/docs/advanced-features/deploy-tokens/) and application ID as GitHub repository secrets:

```bash
uv run fastapi login
uv run fastapi cloud setup-ci --secrets-only --app-id <your-app-id>
```

If the GitHub CLI is installed and authenticated, the command configures `FASTAPI_CLOUD_TOKEN` and `FASTAPI_CLOUD_APP_ID` automatically. Otherwise, it prints the values so you can add them in your repository under **Settings** > **Secrets and variables** > **Actions**.

The workflow runs database migrations and creates the first superuser before deploying. In the repository's **Settings** > **Secrets and variables** > **Actions** page, add these repository variables:

* `PROJECT_NAME`
* `FIRST_SUPERUSER`

Add these repository secrets:

* `DATABASE_URL`
* `SECRET_KEY`
* `FIRST_SUPERUSER_PASSWORD`

Use the same values configured in FastAPI Cloud. For `DATABASE_URL`, use the connection URL from your database provider. The database must be reachable from GitHub-hosted runners so the preparation step can connect to it.

The deployment workflow performs these steps:

1. Installs and builds the frontend into `backend/app/frontend`.
2. Runs `backend/scripts/prestart.sh` to apply database migrations and create the first superuser.
3. Deploys the project with `uv run fastapi deploy`.

## URLs

Replace `your-app.fastapicloud.dev` with the URL of your FastAPI Cloud application.

Application (frontend and API): `https://your-app.fastapicloud.dev`

Interactive API docs: `https://your-app.fastapicloud.dev/docs`

## Docker Compose

For deployment to your own server, see the [Docker Compose deployment guide](./deployment-docker-compose.md).

## GitHub Repository Automation

Install the following GitHub Apps to enable the included repository automation:

* [Latest Changes](https://github.com/apps/latest-changes) updates `release-notes.md` when a pull request is merged.
* [PR Push](https://github.com/apps/pr-push) lets the pre-commit workflow push automated fixes to pull request branches.
* [PR Submit](https://github.com/apps/pr-submit) lets the **Bump pre-commit hooks** and **Prepare Release** workflows create pull requests.

To publish code coverage with [Smokeshow](https://github.com/samuelcolvin/smokeshow), add `SMOKESHOW_AUTH_KEY` as a repository secret.
