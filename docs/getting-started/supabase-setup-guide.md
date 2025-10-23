# Supabase Setup Guide

**Quick reference for setting up Supabase for CurriculumExtractor**

---

## Step 1: Create Supabase Project

1. **Go to Supabase**: https://app.supabase.com
2. Click **"New Project"**
3. Fill in details:
   - **Organization**: Select your organization (or create one)
   - **Name**: `curriculumextractor-dev`
   - **Database Password**: Choose a **strong password** (save this securely!)
   - **Region**: Select closest to your location:
     - **Singapore**: `ap-southeast-1` (Recommended for Singapore)
     - **US East**: `us-east-1`
     - **EU**: `eu-west-1`
   - **Pricing Plan**: Free tier is fine for development

4. Click **"Create new project"**
5. **Wait 2-3 minutes** for project provisioning

---

## Step 2: Get Database Connection String

1. Once project is ready, go to: **Settings → Database**
2. Scroll to **"Connection string"** section
3. Select tab: **"URI"**
4. Toggle: **"Use connection pooling"** → **ON**
5. Select mode: **"Transaction"** (important for IPv6 compatibility)
6. Copy the connection string - it should look like:
   ```
   postgresql://postgres.abcdefghijklmnop:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   ```
   
   **⚠️ Important**: 
   - Replace `[YOUR-PASSWORD]` with the database password you chose in Step 1
   - Keep `:6543` (pooler port) - **NOT** `:5432`
   - Keep the full `postgres.abcdefghijklmnop` format

**Example**:
```
postgresql://postgres.abcdefghijklmnop:MySecurePassword123!@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

---

## Step 3: Get API Credentials

1. Go to: **Settings → API**
2. Find **"Project URL"** section:
   - Copy your project URL (e.g., `https://abcdefghijklmnop.supabase.co`)

3. Find **"Project API keys"** section:
   - Copy **"anon public"** key (starts with `eyJhbG...`)
     - This is safe to use in frontend code
   - Copy **"service_role"** key (starts with `eyJhbG...`)
     - ⚠️ **NEVER expose this in frontend code!**
     - Only use on backend/server

---

## Step 4: Update .env File

Open `/Users/amostan/Repositories/CurriculumExtractor/.env` and replace these lines:

```bash
# Database Connection (from Step 2)
DATABASE_URL=postgresql://postgres.abcdefghijklmnop:MySecurePassword123!@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

# Supabase API Configuration (from Step 3)
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Your actual anon key
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Your actual service role key

# Also update these while you're at it:
FIRST_SUPERUSER_PASSWORD=<choose-a-strong-password>  # Change from 'changethis'
```

**Save the file** after updating.

---

## Step 5: Verify Setup

Run the setup checker:

```bash
cd /Users/amostan/Repositories/CurriculumExtractor
bash scripts/check-setup.sh
```

You should see:
```
✓ Environment setup complete!

🚀 Ready to start development:
   → Run: docker compose watch
   → Open: http://localhost:5173
```

---

## Step 6: Start Development Environment

```bash
cd /Users/amostan/Repositories/CurriculumExtractor
docker compose watch
```

Wait for all services to start (30-60 seconds). You'll see:
```
✔ Container curriculum-extractor-redis-1          Running
✔ Container curriculum-extractor-prestart-1       Exited
✔ Container curriculum-extractor-backend-1        Running
✔ Container curriculum-extractor-celery-worker-1  Running
✔ Container curriculum-extractor-frontend-1       Running
```

---

## Step 7: Access the Application

Open your browser:
- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs

**First Login**:
- **Email**: `admin@curriculumextractor.com` (from FIRST_SUPERUSER)
- **Password**: Whatever you set in `FIRST_SUPERUSER_PASSWORD`

---

## Troubleshooting

### "Connection to PostgreSQL server failed"

**Check**:
1. Verify your database password is correct in `DATABASE_URL`
2. Ensure you're using the **pooler connection** (port `:6543`)
3. Check if Supabase project is active (not paused) in dashboard

**Fix**: Go to Supabase dashboard → Settings → Database → "Connection string" and copy again

### "Invalid JWT token"

**Check**:
1. Verify `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_KEY` are correct
2. Ensure no extra spaces or line breaks in the keys

**Fix**: Go to Settings → API and copy keys again

### "Project paused"

**Issue**: Free tier projects pause after 1 week of inactivity

**Fix**: 
1. Go to Supabase dashboard
2. Click **"Resume project"** button
3. Wait 1-2 minutes
4. Restart `docker compose watch`

---

## Create Storage Buckets (Later)

Once your app is running, you'll need to create storage buckets for PDF uploads:

1. Go to: **Storage** in Supabase dashboard
2. Click **"New bucket"**
3. Create two buckets:
   - Name: `worksheets` (for uploaded PDFs)
     - Public: **No**
     - File size limit: 10 MB
   - Name: `extractions` (for processed data)
     - Public: **No**
     - File size limit: 5 MB

4. Configure Row Level Security (RLS) policies (we'll do this later)

---

## Next Steps

Once your environment is running:
1. ✅ Verify login works at http://localhost:5173
2. ✅ Check API docs at http://localhost:8000/docs
3. 📖 Read `docs/getting-started/development.md` for development workflow
4. 🏗️ Start implementing features from `docs/prd/overview.md`

---

## Security Reminders

⚠️ **Never commit these to git**:
- `.env` file (already in `.gitignore`)
- Database passwords
- `SUPABASE_SERVICE_KEY`

✅ **Safe to expose**:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY` (frontend can use this)

---

**Questions?** Check `SETUP_STATUS.md` or `CLAUDE.md` for more guidance.

