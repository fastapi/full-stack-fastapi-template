# Geo Deployment Plan - Full Stack FastAPI Template

## Epic Details
- **Epic ID**: initial-deploy-01
- **Status**: Planning
- **Target**: Home Server with Cloudflare Tunnel
- **Domain**: TBD

## Goal
Deploy the full-stack FastAPI application to the internet with a custom domain, HTTPS, and email functionality using home server infrastructure with Cloudflare Tunnel for secure exposure.

## High-Level Deployment Tickets

### Phase 1: Infrastructure & Hosting Setup
**Ticket 1.1: Home Server Setup with Cloudflare Tunnel**
- [ ] Verify home server specs and Docker installation
- [ ] Set up Cloudflare account (free tier)
- [ ] Install cloudflared on home server
- [ ] Create Cloudflare Tunnel
- [ ] Configure tunnel ingress rules

**Ticket 1.2: Domain Name Registration and DNS Setup**
- [ ] Choose and register domain name
- [ ] Transfer domain to Cloudflare DNS management
- [ ] Configure CNAME records for tunnel
- [ ] Set up subdomain structure (www, api)

### Phase 2: Server Configuration
**Ticket 2.1: Server Security and Configuration**
- [ ] Update system packages
- [ ] Configure firewall (local access only)
- [ ] Set up automatic security updates
- [ ] Configure Docker resource limits
- [ ] Set up system monitoring

**Ticket 2.2: Cloudflare Tunnel Configuration**
- [ ] Configure tunnel config.yml
- [ ] Set up tunnel as systemd service
- [ ] Test tunnel connectivity
- [ ] Verify SSL certificates (handled by Cloudflare)

### Phase 3: Application Configuration
**Ticket 3.1: Environment Variables for Production** 
- [ ] Generate secure SECRET_KEY
- [ ] Update DOMAIN variable
- [ ] Set FRONTEND_HOST to production URL
- [ ] Configure BACKEND_CORS_ORIGINS
- [ ] Set ENVIRONMENT=production
- [ ] Update PostgreSQL credentials
- [ ] Remove default superuser or change credentials

**Ticket 3.2: Database Setup**
- [ ] Decide on database hosting (same server vs managed service)
- [ ] Set up PostgreSQL with secure credentials
- [ ] Configure database backups
- [ ] Run migrations
- [ ] Test database connectivity

**Ticket 3.3: Email Service Configuration**
- [ ] Choose email service provider (SendGrid, Mailgun, AWS SES, etc.)
- [ ] Create account and verify domain
- [ ] Generate API keys/SMTP credentials
- [ ] Update SMTP settings in environment
- [ ] Configure SPF, DKIM, DMARC records in DNS
- [ ] Test email sending functionality

### Phase 4: Deployment Process
**Ticket 4.1: Code Repository Setup**
- [ ] Push code to GitHub/GitLab (if not already)
- [ ] Set up deployment branch strategy (main/production)
- [ ] Configure .gitignore for production
- [ ] Remove development files from production branch

**Ticket 4.2: Deploy Application**
- [ ] Clone repository to server
- [ ] Create production .env file on server
- [ ] Build Docker images on server
- [ ] Start services with docker-compose
- [ ] Verify all containers are healthy
- [ ] Test application endpoints

**Ticket 4.3: Monitoring & Logging Setup**
- [ ] Configure error tracking (Sentry)
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure log aggregation
- [ ] Set up backup strategy
- [ ] Document recovery procedures

### Phase 5: Performance & Optimization
**Ticket 5.1: Performance Tuning**
- [ ] Configure CDN for static assets (optional)
- [ ] Optimize Docker resource limits
- [ ] Set up Redis for caching (if needed)
- [ ] Configure rate limiting
- [ ] Load test the application

**Ticket 5.2: Security Hardening**
- [ ] Security audit of environment variables
- [ ] Configure CSP headers
- [ ] Set up DDoS protection (Cloudflare)
- [ ] Regular security updates schedule
- [ ] Penetration testing (optional)

### Phase 6: CI/CD & Maintenance
**Ticket 6.1: Continuous Deployment Setup**
- [ ] Configure GitHub Actions for deployment
- [ ] Set up staging environment (optional)
- [ ] Automate database backups
- [ ] Set up health checks
- [ ] Configure rollback procedures

**Ticket 6.2: Documentation & Handoff**
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Document environment variables
- [ ] Create admin user guide
- [ ] Set up knowledge transfer sessions

## Success Criteria
- [ ] Application accessible via HTTPS at custom domain
- [ ] All API endpoints functional
- [ ] Email sending working for password resets
- [ ] Database persisting data correctly
- [ ] Monitoring and alerting in place
- [ ] Backup and recovery tested
- [ ] Documentation complete

## Estimated Timeline
- Phase 1-2: 1-2 days
- Phase 3-4: 2-3 days
- Phase 5-6: 2-3 days
- **Total: ~1 week** for basic production deployment

## Estimated Costs (Monthly)
- Home Server: Electricity ~$5-10/month
- Domain Name: ~$12/year
- Cloudflare Tunnel: FREE
- Email Service: Free tier initially, then $10-25/month
- Optional: Monitoring, Backups: $5-15/month
- **Total: ~$10-35/month** for home-hosted production app

## Next Steps
1. Start with Phase 1 - Set up Cloudflare account and register domain
2. Each ticket can be expanded with detailed subtasks
3. Prioritize security and backups from the beginning
4. Consider starting with a staging deployment first

---

*Note: This plan is designed for home server deployment using Cloudflare Tunnel. Each ticket will be detailed in its respective phase folder as work progresses.*

## Phase Folders
- `phase-1-infrastructure/` - Infrastructure and domain setup tickets
- `phase-2-server-config/` - Server configuration tickets
- `phase-3-app-config/` - Application configuration tickets
- `phase-4-deployment/` - Deployment process tickets
- `phase-5-optimization/` - Performance and security tickets
- `phase-6-cicd/` - CI/CD and maintenance tickets