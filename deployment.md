# FastAPI Project - Deployment

You can deploy the project using Docker Compose in a remote server.

It expects you to have a Traefik proxy handling communication to the outside world and HTTPS certificates.

And you can use CI (continuous integration) systems to deploy automatically.

But you have to configure a couple things first.

## Preparation

* Have a remote server ready and available.
* Configure the DNS records of your domain to point to the IP of the server you just created.
* Install and configure [Docker](https://docs.docker.com/engine/install/).
* Create a remote directory to store your code, for example:

```bash
mkdir -p /root/code/fastapi-project/
```

## Public Traefik

We need a Traefik proxy to handle incoming connections and HTTPS certificates.

### Traefik Docker Compose

Copy the Traefik Docker Compose file to your server, to your code directory. You could do it with `rsync`:

```bash
rsync -a docker-compose.traefik.yml root@your-server.example.com:/root/code/fastapi-project/
```

### Traefik Public Network

This Traefik will expect a Docker "public network" named `traefik-public` to communicate with your stack(s).

This way, there will be a single public Traefik proxy that handles the communication (HTTP and HTTPS) with the outside world, and then behind that, you could have one or more stacks.

To create a Docker "public network" named `traefik-public` run:

```bash
docker network create traefik-public
```

### Traefik Environment Variables

The Traefik Docker Compose file expects some environment variables to be set.

Create the environment variables for HTTP Basic Auth.

* Create the username, e.g.:

```bash
export USERNAME=admin
```

* Create an environment variable with the password, e.g.:

```bash
export PASSWORD=changethis
```

* Use openssl to generate the "hashed" version of the password and store it in an environment variable:

```bash
export HASHED_PASSWORD=$(openssl passwd -apr1 $PASSWORD)
```

* Create an environment variable with the domain name, e.g.:

```bash
export DOMAIN=fastapi-project.example.com
```

* Create an environment variable with the email for Let's Encrypt, e.g.:

```bash
export EMAIL=admin@example.com
```

### Start the Traefik Docker Compose

Now with the environment variables set and the `docker-compose.traefik.yml` in place, you can start the Traefik Docker Compose:

```bash
docker compose -f docker-compose.traefik.yml up -d
```

## Deploy the FastAPI Project

Now that you have Traefik in place you can deploy your FastAPI project with Docker Compose.

You could configure the variables in the `.env` file to match your domain, or you could override them before running the `docker compose` command.

For example:

```bash
export DOMAIN=fastapi-project.example.com
```

And then deploy with Docker Compose:

```bash
docker compose -f docker-compose.yml up -d
```

For production you wouldn't want to have the overrides in `docker-compose.override.yml`, so you would need to explicitly specify the file to use, `docker-compose.yml`.

## Continuous Deployment (CD)

You can use GitHub Actions to deploy your project automatically, and you can have multiple environment deployments, like `staging` and `production`.

* On your remote server, if you are running as the `root` user, create a user for your GitHub Actions:

```bash
adduser github
```

* Add Docker permissions to the `github` user:

```bash
usermod -aG docker github
```

* Temporarily switch to the `github` user:

```bash
su - github
```

* Go to the `github` user's home directory:

```bash
cd
```

* [Install a GitHub Action self-hosted runner following the official guide](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners#adding-a-self-hosted-runner-to-a-repository).

* When asked about labels, add a label for the environment, e.g. `production`.

After installing, the guide would tell you to run a command to start the runner. Nevertheless, it would stop once you terminate that process or if your local connection to your server is lost.

To make sure it runs on startup and continues running, you can install it as a service. To do that, exit the `github` user and go back to the `root` user:

```bash
exit
```

After you do it, you would be on the `root` user again and on the previous directory again belonging to the `root` user.

* Go to the `actions-runner` directory inside of the `github` user's home directory:

```bash
cd /home/github/actions-runner
```

* From there, [install the GitHub Actions runner service following the official guide](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service#installing-the-service):

```bash
./svc.sh install github
```

* Start the service:

```bash
./svc.sh start
```

## GitHub Action Deployment Workflows

There are GitHub Action workflows in the `.github/workflows` directory already configured for deploying to the environments (GitHub Actions runners with the labels):

* `staging`: after pushing (or merging) to the branch `master`.
* `production`: after publishing a release.

## URLs

Replace `fastapi-project.example.com` with your domain:

Frontend: https://fastapi-project.example.com

Backend API docs: https://fastapi-project.example.com/docs

Backend API base URL: https://fastapi-project.example.com/api/

PGAdmin: https://pgadmin.fastapi-project.example.com

Flower: https://flower.fastapi-project.example.com

Traefik UI: https://traefik.fastapi-project.example.com
