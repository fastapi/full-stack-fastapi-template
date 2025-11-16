# Ticket 1.1: Home Server Setup with Cloudflare Tunnel

## Overview
Set up Cloudflare Tunnel (cloudflared) on your home server to securely expose your FastAPI application to the internet without port forwarding.

## Prerequisites
- Home server with SSH access
- Root or sudo privileges
- Docker and Docker Compose installed
- Internet connection

## Step 1: Verify Server Prerequisites

### Check Docker Installation
```bash
docker --version
docker compose version
```
Expected output: Docker version 20+ and Docker Compose version 2+

### Check Available Resources
```bash
# Check RAM
free -h

# Check disk space
df -h

# Check CPU
lscpu | grep "^CPU(s)"
```

## Step 2: Create Cloudflare Account

1. Go to https://dash.cloudflare.com/sign-up
2. Sign up for a free account
3. Verify your email address
4. Log in to the dashboard

## Step 3: Install Cloudflared on Server

### Option A: Install via Package Manager (Recommended)

#### For Ubuntu/Debian:
```bash
# Add Cloudflare GPG key
curl -L https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-archive-keyring.gpg >/dev/null

# Add Cloudflare repository
echo "deb [signed-by=/usr/share/keyrings/cloudflare-archive-keyring.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflared.list

# Update package list
sudo apt update

# Install cloudflared
sudo apt install cloudflared
```


### Verify Installation
```bash
cloudflared --version
```

## Step 4: Authenticate with Cloudflare

```bash
# Login to Cloudflare (opens browser or provides URL)
cloudflared tunnel login
```

**What happens:**
- A browser window will open (or you'll get a URL to visit)
- Select your domain from the list
- Authorize the connection
- A certificate file will be saved to `~/.cloudflared/cert.pem`

### Verify Certificate
```bash
ls -la ~/.cloudflared/cert.pem
```
You should see the cert.pem file listed.

## Step 5: Create the Tunnel

```bash
# Create a tunnel named "fastapi-prod"
cloudflared tunnel create fastapi-prod
```

**Save the output!** You'll see:
- Tunnel ID (a long UUID like: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)
- Credentials file location: `~/.cloudflared/<TUNNEL_ID>.json`
home/home/.cloudflared/219ccc48-4d89-467c-9ea3-f1f39e02ce05.json

### Verify Tunnel Creation
```bash
# List all tunnels
cloudflared tunnel list
```

### Save Your Tunnel ID
```bash
# Create a note of your tunnel ID (replace with your actual ID)
export TUNNEL_ID="your-tunnel-id-here"
echo $TUNNEL_ID
```

## Step 6: Configure the Tunnel

### Create Configuration Directory
```bash
# Ensure cloudflared config directory exists
mkdir -p ~/.cloudflared
```

### Create Tunnel Configuration File
Create `~/.cloudflared/config.yml`:

```bash
nano ~/.cloudflared/config.yml
```

Add the following content (replace YOUR_TUNNEL_ID and YOUR_DOMAIN):

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/YOUR_USERNAME/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  # Frontend - main domain and www
  - hostname: yourdomain.com
    service: http://localhost:5173
  - hostname: www.yourdomain.com
    service: http://localhost:5173

  # Backend API
  - hostname: api.yourdomain.com
    service: http://localhost:8000

  # Catch-all rule (required as last rule)
  - service: http_status:404
```

**Important:**
- Replace `YOUR_TUNNEL_ID` with your actual tunnel ID
- Replace `YOUR_USERNAME` with your server username
- Replace `yourdomain.com` with your actual domain
- Ports 5173 and 8000 should match your docker-compose port mappings

### Verify Configuration Syntax
```bash
# Test the configuration
cloudflared tunnel ingress validate
```

## Step 7: Route DNS to Tunnel

### Option A: Using Cloudflare CLI (Easier)
```bash
# Route your domain to the tunnel
cloudflared tunnel route dns fastapi-prod yourdomain.com
cloudflared tunnel route dns fastapi-prod www.yourdomain.com
cloudflared tunnel route dns fastapi-prod api.yourdomain.com
```

## Step 8: Test the Tunnel

### Start Tunnel Manually (Test Run)
```bash
# Run tunnel in foreground for testing
cloudflared tunnel run fastapi-prod
```

**You should see:**
- Connection established messages
- No error messages
- Tunnel status showing as HEALTHY

Press `Ctrl+C` to stop when verified.

### Test from Another Device
From your phone or another computer (NOT on your home network):
```bash
# Test if DNS is resolving to Cloudflare
nslookup yourdomain.com

# Test if tunnel responds (will show 502 if app isn't running yet - that's OK)
curl -I https://yourdomain.com

```

## Step 9: Install Tunnel as System Service

### Create Systemd Service
```bash
# If you named your config file config.yml
sudo cloudflared service install

# If you named your config file config.yaml, specify the path explicitly
sudo cloudflared --config ~/.cloudflared/config.yaml service install
```

**Note:** Cloudflared looks for `config.yml` by default. If you named it `config.yaml`, you must specify the path with `--config`.

### Start and Enable Service
```bash
# Start the service
sudo systemctl start cloudflared

# Enable on boot
sudo systemctl enable cloudflared

# Check status
sudo systemctl status cloudflared
```

### View Service Logs
```bash
# Follow logs in real-time
sudo journalctl -u cloudflared -f

# View recent logs
sudo journalctl -u cloudflared -n 50
```

## Step 10: Verify Everything Works

### Check Tunnel Status
```bash
# Check if tunnel is running
cloudflared tunnel info fastapi-prod

# List all active connections
cloudflared tunnel list
```

### Test DNS Resolution
```bash
# Test each domain
dig yourdomain.com
dig www.yourdomain.com
dig api.yourdomain.com
```

All should resolve to Cloudflare IPs (not your home IP).

## Troubleshooting

### Tunnel Won't Start
```bash
# Check if cert exists
ls -la ~/.cloudflared/cert.pem

# Check credentials file
ls -la ~/.cloudflared/*.json

# Validate config
cloudflared tunnel ingress validate

# Check for errors
sudo journalctl -u cloudflared -n 100
```

### DNS Not Resolving
```bash
# Check DNS propagation
nslookup yourdomain.com 1.1.1.1

# Verify CNAME records in dashboard
# Go to Cloudflare Dashboard > DNS > Records
```

### 502 Bad Gateway Error
This is expected before your application is running! The tunnel is working, but:
- Your Docker containers aren't running yet, OR
- Ports in config.yml don't match your application

```bash
# Verify your app containers are running
docker ps

# Check if ports are accessible locally
curl http://localhost:8000/api/v1/health
curl http://localhost:5173
```

## Verification Checklist

- [ ] cloudflared installed and version confirmed
- [ ] Successfully logged in to Cloudflare
- [ ] Tunnel created (ID saved)
- [ ] Configuration file created at ~/.cloudflared/config.yml
- [ ] DNS routes configured (CNAME records)
- [ ] Tunnel runs successfully in foreground
- [ ] Systemd service installed and running
- [ ] DNS resolves to Cloudflare (not home IP)
- [ ] Can access domain from external network (502 is OK for now)

## Next Steps

After completing this ticket:
1. Move to Ticket 1.2 for domain registration (if not done)
2. Proceed to Phase 2 for server security configuration
3. Eventually your application will run and tunnel will proxy traffic to it

## Useful Commands Reference

```bash
# Tunnel management
cloudflared tunnel list
cloudflared tunnel info fastapi-prod
cloudflared tunnel delete fastapi-prod

# Service management
sudo systemctl status cloudflared
sudo systemctl restart cloudflared
sudo systemctl stop cloudflared

# Logs
sudo journalctl -u cloudflared -f
sudo journalctl -u cloudflared --since "10 minutes ago"

# Configuration test
cloudflared tunnel ingress validate
cloudflared tunnel ingress rule https://yourdomain.com
```

## Security Notes

- Your home IP is never exposed
- No ports need to be opened on your router
- All traffic is encrypted via Cloudflare
- SSL/TLS certificates are handled automatically by Cloudflare
- Tunnel credentials are stored in ~/.cloudflared/ (keep secure)

## Cost

- Cloudflare Tunnel: FREE
- No bandwidth charges
- No connection limits on free tier