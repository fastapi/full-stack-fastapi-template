# FastAPI Project - Deployment

You can deploy the project using Docker Compose in a remote server.

It expects you to have a main Traefik proxy handling communication to the outside world and HTTPS certificates.

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
