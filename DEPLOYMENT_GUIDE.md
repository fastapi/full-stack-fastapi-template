# AWS EC2 Deployment Guide (IP-based)

This guide will help you deploy your FastAPI project to AWS EC2 using the public IP address.

## Prerequisites

1. AWS EC2 instance running Amazon Linux 2023
2. Security group configured to allow:
   - SSH (port 22)
   - HTTP (port 80)
   - Backend API (port 8000)
   - Adminer (port 8080)
   - Database (port 5432) - optional for external access

## Step 1: Set up EC2 Instance

Connect to your EC2 instance and run these commands:

```bash
# Update the system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again to apply docker group changes
exit
```

## Step 2: Upload Project Files

Upload your project files to the EC2 instance. You can use:

```bash
# From your local machine, upload the project
scp -r -i your-key.pem . ec2-user@YOUR_EC2_IP:/home/ec2-user/mosaic-project/
```

Or clone from Git if your project is in a repository:

```bash
# On the EC2 instance
git clone YOUR_REPOSITORY_URL
cd mosaic-project-cs4800
```

## Step 3: Deploy the Application

1. **Run the deployment script** (replace YOUR_EC2_IP with your actual IP):

```bash
./deploy-ip.sh YOUR_EC2_IP
```

2. **Start the services**:

```bash
docker compose -f docker-compose.production.yml up -d
```

## Step 4: Verify Deployment

Your application will be available at:

- **Frontend**: `http://YOUR_EC2_IP`
- **Backend API**: `http://YOUR_EC2_IP:8000`
- **API Documentation**: `http://YOUR_EC2_IP:8000/docs`
- **Adminer (Database UI)**: `http://YOUR_EC2_IP:8080`

## Step 5: Access the Application

1. **Create your first admin user**:
   - Go to `http://YOUR_EC2_IP:8000/docs`
   - Use the `/api/v1/users/` endpoint to create a user
   - Or use the frontend registration

2. **Login and start using the application**:
   - Frontend: `http://YOUR_EC2_IP`
   - API docs: `http://YOUR_EC2_IP:8000/docs`

## Troubleshooting

### Check if services are running:
```bash
docker compose -f docker-compose.production.yml ps
```

### View logs:
```bash
# All services
docker compose -f docker-compose.production.yml logs

# Specific service
docker compose -f docker-compose.production.yml logs backend
docker compose -f docker-compose.production.yml logs frontend
```

### Restart services:
```bash
docker compose -f docker-compose.production.yml restart
```

### Stop services:
```bash
docker compose -f docker-compose.production.yml down
```

## Security Notes

- The deployment uses HTTP (not HTTPS) since we're using IP addresses
- Database is accessible on port 5432 - consider restricting this in production
- Adminer is accessible on port 8080 - consider restricting this in production
- All passwords are generated securely using Python's secrets module

## Environment Variables

The deployment script automatically generates:
- `SECRET_KEY`: Secure random key for JWT tokens
- `FIRST_SUPERUSER_PASSWORD`: Secure random password for admin user
- `POSTGRES_PASSWORD`: Secure random password for database

You can modify these in the `.env` file if needed.
