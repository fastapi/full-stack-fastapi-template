# Ticket 2.1: Server Security and Configuration

## Overview
Secure your home server with proper firewall rules, automatic updates, resource limits, and monitoring. Since you're using Cloudflare Tunnel, no external ports need to be exposed.

## Prerequisites
- Root or sudo access to home server
- Cloudflare Tunnel already configured and working
- Docker and Docker Compose installed

## Step 1: Update System Packages

### Update Package Lists and Upgrade
```bash
# Update package lists
sudo apt update

# Upgrade all packages
sudo apt upgrade -y

# Upgrade distribution packages
sudo apt dist-upgrade -y

# Remove unnecessary packages
sudo apt autoremove -y
sudo apt autoclean
```

### Check System Info
```bash
# Check Ubuntu version
lsb_release -a

# Check kernel version
uname -r

# Check available disk space
df -h
```

## Step 2: Configure Firewall (UFW)

Since you're using Cloudflare Tunnel, you only need local access and SSH. No web ports (80/443) need to be exposed.

### Install and Configure UFW
```bash
# Install UFW if not already installed
sudo apt install ufw -y

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (IMPORTANT - do this before enabling!)
sudo ufw allow 22/tcp comment 'SSH access'

# Allow SSH from Tailscale network only (more secure)
# Replace with your Tailscale subnet if you want to restrict SSH to Tailscale only
# sudo ufw allow from 100.64.0.0/10 to any port 22 proto tcp comment 'SSH via Tailscale'

# Allow mDNS for local network discovery (optional)
sudo ufw allow 5353/udp comment 'mDNS'

# Check rules before enabling
sudo ufw show added
```

### Enable Firewall
```bash
# Enable UFW
sudo ufw enable

# Check status
sudo ufw status verbose

# Check numbered list (useful for deleting rules later)
sudo ufw status numbered
```

### Important Notes:
- Port 80/443: NOT needed (Cloudflare Tunnel handles external traffic)
- Port 22: SSH access (consider Tailscale-only access for extra security)
- All Docker ports: Accessible on localhost only
- Pi-hole: Accessible via localhost and Tailscale only

## Step 3: Set Up Automatic Security Updates

### Install unattended-upgrades
```bash
# Install package
sudo apt install unattended-upgrades -y

# Configure automatic updates
sudo dpkg-reconfigure -plow unattended-upgrades
# Select "Yes" when prompted
```

### Configure Update Settings
```bash
# Edit configuration
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
```

Ensure these lines are uncommented:
```
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";  // Set to true if you want auto-reboot
```

### Enable Automatic Updates
```bash
# Create/edit auto-upgrade config
sudo nano /etc/apt/apt.conf.d/20auto-upgrades
```

Add this content:
```
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
```

### Test Configuration
```bash
# Dry run to test
sudo unattended-upgrades --dry-run --debug

# Check status
sudo systemctl status unattended-upgrades
```

## Step 4: Configure Docker Resource Limits

### Create Docker Daemon Configuration
```bash
# Edit Docker daemon config
sudo nano /etc/docker/daemon.json
```

Add resource limits:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  },
  "storage-driver": "overlay2",
  "userland-proxy": false
}
```

### Restart Docker
```bash
# Restart Docker service
sudo systemctl restart docker

# Verify configuration
sudo docker info | grep -A 10 "Log"
```

### Set Container Resource Limits in Docker Compose

For your production deployment, you can add resource limits. Create a `docker-compose.production.yml`:

```bash
nano ~/full-stack-fastapi-template/docker-compose.production.yml
```

Add content:
```yaml
version: "3.8"

services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    restart: unless-stopped

  frontend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    restart: unless-stopped

  db:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    restart: unless-stopped
```

## Step 5: Set Up System Monitoring

### Install Monitoring Tools
```bash
# Install htop for interactive monitoring
sudo apt install htop -y

# Install iotop for disk I/O monitoring
sudo apt install iotop -y

# Install nethogs for network monitoring
sudo apt install nethogs -y

# Install glances (all-in-one monitoring)
sudo apt install glances -y
```

### Monitor Docker
```bash
# Real-time container stats
docker stats

# View logs for all containers
docker compose -f ~/full-stack-fastapi-template/docker-compose.yml logs -f

# Check disk usage by Docker
docker system df

# Clean up unused Docker resources
docker system prune -a --volumes
```

### Set Up Log Rotation for Application Logs
```bash
# Check current log rotation config
sudo nano /etc/logrotate.d/docker-containers
```

Add:
```
/var/lib/docker/containers/*/*.log {
  rotate 7
  daily
  compress
  size=10M
  missingok
  delaycompress
  copytruncate
}
```

## Step 6: Additional Security Hardening

### Disable Root SSH Login (Optional but Recommended)
```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config
```

Change or add:
```
PermitRootLogin no
PasswordAuthentication no  # If using SSH keys
PubkeyAuthentication yes
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

### Install and Configure Fail2Ban
```bash
# Install fail2ban
sudo apt install fail2ban -y

# Create local configuration
sudo nano /etc/fail2ban/jail.local
```

Add:
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
logpath = %(sshd_log)s
backend = %(sshd_backend)s
```

Start fail2ban:
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Check status
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

### Set Up Email Alerts for Security Events (Optional)
```bash
# Install mailutils
sudo apt install mailutils -y

# Configure for login alerts
sudo nano /etc/profile.d/login-alert.sh
```

Add:
```bash
#!/bin/bash
if [ -n "$SSH_CLIENT" ]; then
    IP=$(echo $SSH_CLIENT | awk '{print $1}')
    echo "SSH Login: $USER from $IP on $(hostname) at $(date)" | logger -t ssh-login
fi
```

Make executable:
```bash
sudo chmod +x /etc/profile.d/login-alert.sh
```

## Step 7: Verify Security Configuration

### Check Firewall
```bash
# Verify UFW status
sudo ufw status verbose

# Check listening ports
sudo ss -tulpn

# Should only see:
# - SSH (22) if enabled
# - Docker internal ports on 127.0.0.1
# - Pi-hole on port 80 (127.0.0.1)
```

### Verify Docker
```bash
# Check Docker service
sudo systemctl status docker

# Verify resource limits
docker info | grep -i memory
docker info | grep -i cpu
```

### Check System Updates
```bash
# Verify unattended-upgrades
sudo systemctl status unattended-upgrades

# Check update logs
sudo tail -f /var/log/unattended-upgrades/unattended-upgrades.log
```

### System Health Check
```bash
# Check system load
uptime

# Check memory usage
free -h

# Check disk usage
df -h

# Check running services
sudo systemctl list-units --type=service --state=running
```

## Step 8: Create Monitoring Script

### Create Health Check Script
```bash
nano ~/server-health-check.sh
```

Add:
```bash
#!/bin/bash

echo "=== Server Health Check ==="
echo "Date: $(date)"
echo ""

echo "=== Uptime ==="
uptime
echo ""

echo "=== Memory Usage ==="
free -h
echo ""

echo "=== Disk Usage ==="
df -h /
echo ""

echo "=== Docker Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Size}}"
echo ""

echo "=== Cloudflare Tunnel Status ==="
sudo systemctl status cloudflared --no-pager | head -10
echo ""

echo "=== Recent Failed SSH Attempts ==="
sudo journalctl -u ssh -S today | grep -i failed | tail -5
echo ""

echo "=== Firewall Status ==="
sudo ufw status
echo ""
```

Make executable and run:
```bash
chmod +x ~/server-health-check.sh
~/server-health-check.sh
```

### Create Cron Job for Daily Health Checks (Optional)
```bash
# Edit crontab
crontab -e
```

Add:
```
# Daily health check at 8 AM
0 8 * * * ~/server-health-check.sh >> ~/health-check.log 2>&1
```

## Verification Checklist

- [ ] System packages updated to latest versions
- [ ] UFW firewall enabled with proper rules
- [ ] No unnecessary ports exposed (check with `sudo ss -tulpn`)
- [ ] Automatic security updates configured
- [ ] Docker resource limits set
- [ ] Monitoring tools installed
- [ ] Fail2ban configured for SSH protection
- [ ] Docker logs rotating properly
- [ ] Health check script created and working
- [ ] Cloudflare Tunnel still running after changes

## Testing Your Security

### Port Scan from External Network
From another computer or phone (not on your home network):
```bash
# Should timeout or show filtered for all ports except those you've explicitly opened
nmap -Pn your-home-ip-address
```

Expected result: All ports should be filtered/closed.

### Verify Cloudflare Tunnel Still Works
```bash
# Check tunnel status
curl -I https://a-seashell-company.com

# Should return 502 (app not running) or 200 (if app is running)
# Should NOT timeout or fail to resolve
```

## Maintenance Commands

```bash
# Weekly security updates check
sudo apt update && sudo apt list --upgradable

# Monthly Docker cleanup
docker system prune -a --volumes

# Check fail2ban bans
sudo fail2ban-client status sshd

# View firewall logs
sudo tail -f /var/log/ufw.log

# Monitor system resources
htop
glances
```

## Security Best Practices

1. **Regular Updates**: Run `sudo apt update && sudo apt upgrade` monthly
2. **Monitor Logs**: Check `sudo journalctl -xe` for system errors
3. **Docker Cleanup**: Run `docker system prune` monthly
4. **Backup**: Set up regular backups of your data
5. **SSH Keys Only**: Disable password authentication
6. **Tailscale for Admin**: Use Tailscale for SSH access when possible
7. **Monitor Fail2Ban**: Check for unusual login attempts

## Troubleshooting

### Firewall Blocking Something Important
```bash
# Temporarily disable firewall
sudo ufw disable

# Re-enable after testing
sudo ufw enable
```

### Docker Not Starting After Resource Limits
```bash
# Check Docker logs
sudo journalctl -u docker -n 50

# Reset Docker config if needed
sudo mv /etc/docker/daemon.json /etc/docker/daemon.json.bak
sudo systemctl restart docker
```

### SSH Locked Out
If you accidentally lock yourself out:
- Use Tailscale to access the server
- Use physical access to the server
- Reboot into recovery mode if needed

## Next Steps

After completing this ticket:
1. Ticket 2.2 is already complete (Cloudflare Tunnel configured in Phase 1)
2. Move to Phase 3 for application configuration
3. Set up production environment variables
4. Configure email service
5. Deploy your application

## Cost

All tools and configurations in this ticket are FREE and open source.