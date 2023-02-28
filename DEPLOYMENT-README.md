# Step-by-step production deployment guide

There are easier ways to run a blog. You will find the resource requirements for this stack quite substantive. This really is if you intend to run some complex web service and need all the architecture.

> **NOTE**: this is a more focused, step-by-step version of the generated "README". You will find a few more details there, especially about customising larger deployments, or changing your configuration after deployment. This is designed to get you up-and-running with your first production deployment in a controlled way. No guarantees, though.

## Preparation

### Committing to GitHub

Prepare your code and resources for your first commit. There are three files which must **not** be committed unless you're quite positive your data will never leak.

- `/.env`
- `/cookiecutter-config-file.yml`
- `/frontend/.env`

These files will also need to be customised for production deployment. Make alternative arrangements for these files. Don't trust `.gitignore` to save you.

### DigitalOcean Droplets

This guide uses [DigitalOcean Droplets](https://www.digitalocean.com/pricing/droplets), so customise as required. Deploy to the smallest (currently 500MiB memory, 1 vCPU and 10GiB SSD for $4/month). You can upgrade later when you know your resource requirements.

> **WARNING**: if you're using `neo4j` then the `java` server alone will need 1Gb of memory, and you may need a 2Gb to 4Gb base droplet. Plan accordingly. If you decide not to use it, you will need to carefully remove it. That will require editing `docker-compose.yml` and the start-up sequence in the backend. Shouldn't be too challenging.

Ensure you add your SSH encryption keys on launch so that your server can be secure from the beginning.

Deploy on whatever server image your prefer, although the default would be Ubuntu 20.04 (22.04 is the latest). End-of-life for 20.04 is April 2030, and for 22.04 is April 2032. You have time. The underlying image isn't that critical, as you'll be using the Docker images at their current versions.

### Domain name and email

Get your settings and redirects at your registrar, and then set up the various DNS records at DigitalOcean, pointing at the IP address for the droplet you set up.

For reference: 
- [Link Namecheap domain to DigitalOcean](https://www.namecheap.com/support/knowledgebase/article.aspx/10375/2208/how-do-i-link-a-domain-to-my-digitalocean-account/)
- [Manage DNS records at DigitalOcean](https://docs.digitalocean.com/products/networking/dns/how-to/manage-records/)

Don't forget to create DNS A records for `flower`, `neo4j`, `traefik`, and `pgadmin`.

Now you should be able to login to your server and begin deployment.

## Deployment

### Docker

Update your server, and install all required packages:

```shell
# Install the latest updates
apt-get update
apt-get upgrade -y
```

Then:

```shell
# Download Docker 
curl -fsSL get.docker.com -o get-docker.sh
# Install Docker using the stable channel (instead of the default "edge") 
CHANNEL=stable sh get-docker.sh
# Remove Docker install script 
rm get-docker.sh
```

### Clone your repository

The basic approach is to clone from GitHub then set up the appropriate `.env` files and any custom `conf` files called from `docker-compose`. If yours is a private repo, review the GitHub docs for how to set that up.

Remember you can create new passwords as follows:

```bash
openssl rand -hex 32
# Outputs something like: 99d3b1f01aa639e4a76f4fc281fc834747a543720ba4c8a8648ba755aef9be7f
```

From `/srv`:

```shell
git clone https://github.com/<user-name>/<project-name>.git
```

Then continue from the project directory `/srv/<project-name>`. You can always pull your latest code from that directory, with:

```shell
git pull
```

### Docker Swarm Mode

Deploy the stack to a Docker Swarm mode cluster with a main Traefik proxy, set up using the ideas from [DockerSwarm.rocks](https://dockerswarm.rocks). And you can use CI (continuous integration) systems to do it automatically.

This stack expects the public Traefik network to be named `traefik-public`.

```bash
export USE_HOSTNAME=example.com
```

```bash
# Set up the server hostname 
echo $USE_HOSTNAME > /etc/hostname 
hostname -F /etc/hostname
```

Set up **Swarm Mode**:

```shell
docker swarm init
```

If this fails, you'll need to explicitly link the public IP for the droplet:

```shell
docker swarm init --advertise-addr 123.123.123.123
```

You can add additional manager and worker nodes. This is optional and you can read the DockerSwarm.rocks link for more.

Check that the nodes are connected and running:

```shell
docker node ls
```

Which would output something like:

```
ID                            HOSTNAME             STATUS    AVAILABILITY    MANAGER STATUS    ENGINE VERSION
ndcg2iavasdfrm6q2qwere2rr *   dog.example.com      Ready     Active          Leader            18.06.1-ce
```

### Traefik Proxy with HTTPS

Follow the documentation from DockerSwarm.rocks to [get automatic HTTPS certificates](https://dockerswarm.rocks/traefik/).

Create a network that will be shared with Traefik and the containers that should be accessible from the outside, with

```shell
docker network create --driver=overlay traefik-public
```

Get the Swarm node ID of this node and store it in an environment variable (use the code below exactly):

```shell
export NODE_ID=$(docker info -f '{{.Swarm.NodeID}}')
```

Create a tag in this node, so that Traefik is always deployed to the same node and uses the same volume:

```shell
docker node update --label-add traefik-public.traefik-public-certificates=true $NODE_ID
```

Create an environment variable with your email, to be used for the generation of Let's Encrypt certificates, e.g.:

```shell
export EMAIL=someone@example.com
```

Create an environment variable with the domain you want to use for the Traefik UI (user interface), e.g.:

```shell
export DOMAIN=traefik.example.com
```

You will access the Traefik dashboard at this domain, e.g. `traefik.example.com`.

Create an environment variable with a username (you will use it for the HTTP Basic Auth for Traefik and Consul UIs), for example:

```shell
export USERNAME=admin
```

Create an environment variable with the password, e.g.:

```shell
export PASSWORD=changethis
```

Use `openssl` to generate the "hashed" version of the password and store it in an environment variable:

```shell
export HASHED_PASSWORD=$(openssl passwd -apr1 $PASSWORD)
```

Download the file `traefik.yml`:

```shell
curl -L dockerswarm.rocks/traefik.yml -o traefik.yml
```

Deploy the stack with:

```shell
docker stack deploy -c traefik.yml traefik
```

It will use the environment variables you created above. Check if the stack was deployed with:

```bash
docker stack ps traefik
```

It will output something like:

```
ID             NAME                IMAGE          NODE              DESIRED STATE   CURRENT STATE          ERROR   PORTS
w5o6fmmln8ni   traefik_traefik.1   traefik:v2.2   dog.example.com   Running         Running 1 minute ago
```

You can check the Traefik logs with:

```bash
docker service logs traefik_traefik
```

### Deploy to a Docker Swarm mode cluster

There are 4 (5) steps:

1. **Pull** your git repo
2. **Build** your app images
3. **Deploy** your stack
4. **Restart** your docker service

---

Here are the steps in detail:

1. **Pull** your git repo

```bash
cd /srv/example
```
```bash
sudo git pull
```

2. **Build your app images**

* Set these environment variables, right before the next command:
  * `TAG=prod`
  * `FRONTEND_ENV=production`
* Use the provided `scripts/build.sh` file with those environment variables:

```bash
TAG=prod DOMAIN=example.com STACK_NAME=example-com TRAEFIK_TAG=example.com FRONTEND_ENV=production bash -x scripts/build.sh
```

**Persisting Docker named volumes**

You can use [`docker-auto-labels`](https://github.com/tiangolo/docker-auto-labels) to automatically read the placement constraint labels in your Docker stack (Docker Compose file) and assign them to a random Docker node in your Swarm mode cluster if those labels don't exist yet.

To do that, you can install `docker-auto-labels`:

```bash
pip install docker-auto-labels
```

And then run it passing your `docker-stack.yml` file as a parameter:

```bash
docker-auto-labels docker-stack.yml
```

You can run that command every time you deploy, right before deploying, as it doesn't modify anything if the required labels already exist.

3. **Deploy your stack**

* Set these environment variables:
  * `DOMAIN=example.com`
  * `TRAEFIK_TAG=example.com`
  * `STACK_NAME=example-com`
  * `TAG=prod`
* Use the provided `scripts/deploy.sh` file with those environment variables:

```bash
DOMAIN=example.com TRAEFIK_TAG=example.com STACK_NAME=example-com TAG=prod bash -x scripts/deploy.sh
```

4. **Restart** your docker service

```bash
sudo service docker restart
```

You may need to prune regularly while developing if you find yourself running out of space:

```shell
docker system prune
```

## URLs

These are the URLs that will be used and generated by the project.

### Production URLs

Production URLs, from the branch `production`.

Frontend: https://example.com

Backend: https://example.com/api/

Automatic Interactive Docs (Swagger UI): https://example.com/docs

Automatic Alternative Docs (ReDoc): https://example.com/redoc

PGAdmin: https://pgadmin.example.com

Flower: https://flower.example.com

Traefik: https://traefik.example.com