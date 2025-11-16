# Ticket 3.3: Email Service Configuration

## Overview
Configure an email service provider (SMTP) to enable password reset emails, user notifications, and other email functionality in your FastAPI application.

## Prerequisites
- Domain name configured (a-seashell-company.com)
- Access to domain DNS settings in Cloudflare
- Application environment variables configured (Ticket 3.1)

## Step 1: Set Up SendGrid Account

This project uses **SendGrid** for email delivery (100 emails/day free tier).

### Create Account
1. Go to https://sendgrid.com/
2. Click **Start for Free**
3. Sign up with your email
4. Verify your email address
5. Complete the signup process

### Create API Key
1. Log in to SendGrid dashboard
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Name it: `seashell-company-prod`
5. Select **Full Access** (or **Restricted Access** with Mail Send permissions)
6. Click **Create & View**
7. **COPY THE API KEY NOW** - you won't see it again!
8. Save it securely (password manager)

### Verify Sender Email (Single Sender)

For small projects, use Single Sender Verification:

1. Go to **Settings** → **Sender Authentication**
2. Click **Get Started** under **Sender Identity**
3. Choose **Single Sender Verification**
4. Fill in details:
   ```
   From Name: A Seashell Company
   From Email Address: noreply@a-seashell-company.com
   Reply To: support@a-seashell-company.com (or your actual email)
   Company Address: Your address
   ```
5. Click **Create**
6. Check your inbox for verification email
7. Click verification link

### Domain Authentication (Recommended for Production)

For better deliverability:

1. Go to **Settings** → **Sender Authentication**
2. Click **Get Started** under **Domain Authentication**
3. Select DNS host: **Cloudflare**
4. Enter domain: `a-seashell-company.com`
5. Click **Next**
6. SendGrid will show DNS records to add

**Keep this page open - you'll add these records in Step 2**

## Step 2: Configure DNS Records in Cloudflare

### Add SendGrid DNS Records

1. Open Cloudflare dashboard: https://dash.cloudflare.com
2. Select your domain: `a-seashell-company.com`
3. Go to **DNS** → **Records**

SendGrid has provided these specific DNS records for your domain:

**CNAME Records to Add:**

1. **Tracking/Click Domain:**
```
Type: CNAME
Name: url2852
Target: sendgrid.net
Proxy: DNS only (grey cloud)
```

2. **SendGrid Subdomain:**
```
Type: CNAME
Name: 57330946
Target: sendgrid.net
Proxy: DNS only (grey cloud)
```

3. **Email Subdomain:**
```
Type: CNAME
Name: em2172
Target: u57330946.wl197.sendgrid.net
Proxy: DNS only (grey cloud)
```

4. **DKIM Key 1:**
```
Type: CNAME
Name: s1._domainkey
Target: s1.domainkey.u57330946.wl197.sendgrid.net
Proxy: DNS only (grey cloud)
```

5. **DKIM Key 2:**
```
Type: CNAME
Name: s2._domainkey
Target: s2.domainkey.u57330946.wl197.sendgrid.net
Proxy: DNS only (grey cloud)
```

**Add each record:**
1. Click **Add record**
2. Select **CNAME**
3. Enter Name (just the subdomain part)
4. Enter Target (from SendGrid)
5. Set Proxy status to **DNS only** (grey cloud)
6. Click **Save**

### Verify DNS Records

Back in SendGrid:
1. Click **Verify** button
2. Wait a few minutes for DNS propagation
3. Should show "Verified" status

If verification fails:
- Wait 5-10 minutes for DNS propagation
- Check records are correct in Cloudflare
- Ensure Proxy is OFF (grey cloud)

### Add SPF Record (if not exists)

Check if you have SPF record:
```bash
# From your laptop
dig TXT a-seashell-company.com | grep spf
```

If no SPF record exists, add in Cloudflare:
```
Type: TXT
Name: @
Content: v=spf1 include:sendgrid.net ~all
```

If SPF record exists, add `include:sendgrid.net` to it:
```
v=spf1 include:sendgrid.net include:other-service.com ~all
```

### Add DMARC Record

SendGrid also provided a DMARC record:

```
Type: TXT
Name: _dmarc
Content: v=DMARC1; p=none;
Proxy: DNS only (grey cloud)
```

This tells email providers what to do with failed authentication. The `p=none` policy means monitor only (don't reject emails that fail).

## Step 3: Update Application Environment Variables

### Edit .env File on Server

```bash
# SSH into your server
# Navigate to project
cd ~/full-stack-fastapi-template

# Edit .env
nano .env
```

### Update Email Variables

Find the SMTP section and update:

```bash
# Email Configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.your-actual-api-key-here
SMTP_TLS=True
SMTP_SSL=False
EMAILS_FROM_EMAIL=noreply@a-seashell-company.com
```

**Important:**
- `SMTP_USER` is literally the word `apikey` (not your username)
- `SMTP_PASSWORD` is your SendGrid API key
- `EMAILS_FROM_EMAIL` must match verified sender

### Verify Configuration

```bash
# Check updated values (be careful - contains secrets!)
grep -E '^SMTP_|^EMAILS_FROM' .env

# Should show all SMTP variables filled in
```

## Step 4: Restart Application

### Restart Backend Container
```bash
cd ~/full-stack-fastapi-template

# Restart to load new env variables
docker compose restart backend

# Check logs for errors
docker compose logs backend | grep -i "email\|smtp"
```

### Verify Email Configuration Loaded

```bash
# Check if backend sees SMTP configuration
docker compose exec backend python -c "
from app.core.config import settings
print(f'SMTP Host: {settings.SMTP_HOST}')
print(f'SMTP Port: {settings.SMTP_PORT}')
print(f'Emails enabled: {settings.emails_enabled}')
print(f'From email: {settings.EMAILS_FROM_EMAIL}')
"
```

Should output:
```
SMTP Host: smtp.sendgrid.net
SMTP Port: 587
Emails enabled: True
From email: noreply@a-seashell-company.com
```

## Step 5: Test Email Sending

### Test via API Endpoint

The app has a test email endpoint. Use it:

```bash
# From your laptop or server
curl -X POST https://api.a-seashell-company.com/api/v1/utils/test-email \
  -H "Content-Type: application/json" \
  -d '{"email_to": "your-actual-email@example.com"}'
```

Replace `your-actual-email@example.com` with your real email.

### Check for Email

1. Check your inbox
2. Check spam folder
3. Should receive test email within 1-2 minutes

### Test Password Recovery Flow

1. Go to https://a-seashell-company.com
2. Click **Forgot Password**
3. Enter your admin email
4. Check inbox for password reset email
5. Click link and reset password

### Check SendGrid Activity

1. Go to SendGrid dashboard
2. Click **Activity** in sidebar
3. Should see recent email sends
4. Check delivery status

## Step 6: Verify Deliverability

### Test Email Spam Score

Send test email to: https://www.mail-tester.com/

1. Go to mail-tester.com
2. Copy the email address shown
3. Send test email from your app to that address
4. Click **Then check your score** on mail-tester
5. Should score 8+/10

If score is low:
- Verify SPF, DKIM, DMARC records
- Check domain authentication in SendGrid
- Ensure sender email is verified

### Monitor Email Logs

```bash
# View backend logs for email activity
docker compose logs backend -f | grep -i "email\|smtp"

# Look for successful sends or errors
```

## Verification Checklist

- [ ] Email service provider account created
- [ ] API key generated and saved securely
- [ ] Sender email verified
- [ ] Domain authentication configured (recommended)
- [ ] DNS records added to Cloudflare
- [ ] DNS records verified
- [ ] SPF record configured
- [ ] DMARC record added
- [ ] .env file updated with SMTP settings
- [ ] Backend container restarted
- [ ] Email configuration loaded correctly
- [ ] Test email sent successfully
- [ ] Password reset email works
- [ ] Email deliverability tested
- [ ] SendGrid activity shows successful sends

## Troubleshooting

### Emails Not Sending

**Check Backend Logs:**
```bash
docker compose logs backend | tail -50
```

Look for errors like:
- Authentication failed
- Connection refused
- Invalid credentials

**Common Issues:**

1. **Wrong API Key:**
   - Verify SMTP_PASSWORD is correct API key
   - Regenerate API key if needed

2. **Unverified Sender:**
   - Check sender email is verified in SendGrid
   - EMAILS_FROM_EMAIL must match verified email

3. **SMTP Settings Wrong:**
   - SMTP_USER should be `apikey` (literally)
   - SMTP_PORT should be `587`
   - SMTP_TLS should be `True`

4. **emails_enabled is False:**
   ```bash
   # Check if emails are enabled
   docker compose exec backend python -c "
   from app.core.config import settings
   print(settings.emails_enabled)
   "
   ```
   Should print `True`. If `False`, check SMTP_HOST and EMAILS_FROM_EMAIL are both set.

### Emails Going to Spam

**Fix:**
1. Verify domain authentication in SendGrid
2. Add SPF, DKIM, DMARC records
3. Use verified domain for sender
4. Don't use words like "test" in subject
5. Include unsubscribe link
6. Warm up sending (start slow)

### DNS Records Not Verifying

**Wait longer:**
- DNS propagation can take 5-30 minutes
- Try again after waiting

**Check records:**
```bash
# Check CNAME records
dig CNAME s1._domainkey.a-seashell-company.com

# Should return SendGrid target
```

**Common mistakes:**
- Proxy enabled (should be DNS only/grey cloud)
- Wrong Name (don't include full domain)
- Copy-paste errors in Target

## Security Best Practices

1. **Secure API Keys:**
   - Never commit to git
   - Store in password manager
   - Rotate periodically

2. **Rate Limiting:**
   - Monitor SendGrid usage
   - Implement rate limiting in app
   - Prevent abuse

3. **Sender Verification:**
   - Always verify sender domain
   - Use domain authentication
   - Don't spoof sender addresses

4. **Content Security:**
   - Sanitize user input in emails
   - Use templates
   - Avoid sensitive data in emails

## Monitoring Email Usage

### SendGrid Dashboard
- **Activity Feed**: See all sent emails
- **Statistics**: Delivery rates, opens, clicks
- **Alerts**: Set up for delivery issues

### Set Usage Alerts
1. Go to SendGrid **Settings** → **Alerts**
2. Set alert at 80% of quota
3. Enter your email for notifications

### Backend Logs
```bash
# Monitor email sending
docker compose logs backend -f | grep "email"
```

## Cost Considerations

**SendGrid Free Tier:**
- 100 emails/day = 3,000/month
- Sufficient for small apps
- Upgrade to $15/month for 50,000 emails

**When to Upgrade:**
- Approaching daily limit
- Need better analytics
- Want dedicated IP
- Higher deliverability requirements

## Next Steps

After completing this ticket:
1. All Phase 3 tickets complete
2. Move to Phase 4: Deployment
3. Deploy application with full configuration
4. Test all email flows in production
5. Monitor email deliverability

## Additional Resources

- [SendGrid Documentation](https://docs.sendgrid.com/)
- [Email Deliverability Guide](https://sendgrid.com/resource/email-deliverability-guide/)
- [SPF, DKIM, DMARC Explained](https://www.cloudflare.com/learning/email-security/dmarc-dkim-spf/)
- [Mail-Tester](https://www.mail-tester.com/) - Test email spam score