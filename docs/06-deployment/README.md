# Deployment Guide

This guide explains how to deploy the Full Stack FastAPI Template to a production environment using Docker Compose.

## Overview

The deployment strategy uses:

- **Docker Compose**: For container orchestration
- **Traefik**: As a reverse proxy handling HTTPS certificates
- **GitHub Actions**: For continuous deployment (optional)

## Prerequisites

Before deploying, ensure you have:

- A remote server with SSH access
- Docker and Docker Compose installed on the server
- A domain name with DNS configured to point to your server
- Basic understanding of Linux commands and Docker

## Deployment Process

### 1. Prepare Your Server

#### Set Up Docker

Install Docker on your server following the [official Docker installation guide](https://docs.docker.com/engine/install/).

#### Create a Network for Traefik

Create a Docker network for Traefik to communicate with your services:

```bash
docker network create traefik-public
```

### 2. Configure Traefik

Traefik will handle incoming connections and HTTPS certificates.

#### Traefik Setup

Copy the `docker-compose.traefik.yml` to your server:

```bash
mkdir -p /root/code/traefik-public/
scp docker-compose.traefik.yml root@your-server.example.com:/root/code/traefik-public/
```

#### Set Traefik Environment Variables

```bash
export USERNAME=admin  # For Traefik Dashboard
export PASSWORD=changethis  # Use a secure password
export HASHED_PASSWORD=$(openssl passwd -apr1 $PASSWORD)
export DOMAIN=yourdomain.com
export EMAIL=admin@yourdomain.com  # For Let's Encrypt
```

#### Start Traefik

```bash
cd /root/code/traefik-public/
docker compose -f docker-compose.traefik.yml up -d
```

### 3. Configure Your Application

#### Create Environment Variables

Set the necessary environment variables for your application:

```bash
# Environment (staging or production)
export ENVIRONMENT=production

# Domain for your application
export DOMAIN=yourdomain.com

# Stack name for Docker Compose
export STACK_NAME=yourdomain-com

# Application configuration
export PROJECT_NAME="Your Project Name"
export SECRET_KEY="your-secure-secret-key"  # Generate with command below
export FIRST_SUPERUSER="admin@example.com"
export FIRST_SUPERUSER_PASSWORD="your-secure-password"

# Database configuration
export POSTGRES_PASSWORD="your-secure-db-password"

# Email configuration (if needed)
export SMTP_HOST=smtp.example.com
export SMTP_USER=user
export SMTP_PASSWORD=password
export EMAILS_FROM_EMAIL=info@example.com
```

To generate secure keys:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Deploy Your Application

#### Copy files to the server

```bash
scp docker-compose.yml root@your-server.example.com:/root/app/
```

#### Deploy with Docker Compose

```bash
cd /root/app/
docker compose -f docker-compose.yml up -d
```

## Continuous Deployment with GitHub Actions

You can set up GitHub Actions for automated deployments.

### 1. Install GitHub Actions Runner

On your server:

```bash
# Create a user for GitHub Actions
sudo adduser github
sudo usermod -aG docker github

# Switch to the github user
sudo su - github
cd

# Install the GitHub Actions runner
# Follow the GitHub instructions for adding a self-hosted runner
# https://docs.github.com/en/actions/hosting-your-own-runners
```

Install the runner as a service:

```bash
sudo su
cd /home/github/actions-runner
./svc.sh install github
./svc.sh start
./svc.sh status
```

### 2. Configure GitHub Secrets

In your GitHub repository, add the following secrets:

- `DOMAIN_PRODUCTION`: Your production domain
- `DOMAIN_STAGING`: Your staging domain (if applicable)
- `STACK_NAME_PRODUCTION`: Stack name for production
- `STACK_NAME_STAGING`: Stack name for staging (if applicable)
- `EMAILS_FROM_EMAIL`: Email sender address
- `FIRST_SUPERUSER`: Admin user email
- `FIRST_SUPERUSER_PASSWORD`: Admin user password
- `POSTGRES_PASSWORD`: Database password
- `SECRET_KEY`: Application secret key

### 3. GitHub Workflows

The repository includes GitHub workflows for:

- **Staging deployment**: Triggered by pushes to the `master` branch
- **Production deployment**: Triggered by publishing a release

## Access Your Application

After deployment, your services will be available at:

- **Frontend**: `https://dashboard.yourdomain.com`
- **API**: `https://api.yourdomain.com`
- **API Docs**: `https://api.yourdomain.com/docs`
- **Adminer**: `https://adminer.yourdomain.com`
- **Traefik Dashboard**: `https://traefik.yourdomain.com`

## Troubleshooting

### Check Logs

```bash
# View logs for all services
docker compose logs

# View logs for a specific service
docker compose logs backend
docker compose logs frontend
docker compose logs traefik
```

### Check Container Status

```bash
docker compose ps
```

### Restart Services

```bash
docker compose restart
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart containers
docker compose down
docker compose up -d --build
```

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)