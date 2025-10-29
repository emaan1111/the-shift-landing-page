# 🐘 PostgreSQL Setup for Mac (Local Development)

## Quick Start - Install PostgreSQL Locally

### Option 1: Homebrew (Recommended - Easiest)

```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Create your database
createdb analytics_db

# Test connection
psql analytics_db
```

### Option 2: Postgres.app (GUI - User Friendly)

1. Download from: https://postgresapp.com/
2. Move to Applications folder
3. Double-click to start
4. Click "Initialize" to create a new server
5. Your database URL will be: `postgresql://localhost/postgres`

### Option 3: Docker (If you prefer containers)

```bash
# Run PostgreSQL in Docker
docker run --name analytics-postgres \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=analytics_db \
  -p 5432:5432 \
  -d postgres:15

# Connect
psql postgresql://postgres:mypassword@localhost:5432/analytics_db
```

---

## Set Up Your Local Database

### Step 1: Create Database

```bash
# Using Homebrew installation
createdb analytics_db

# OR using psql
psql postgres
CREATE DATABASE analytics_db;
\q
```

### Step 2: Set Environment Variable

**Option A: Add to your shell profile (permanent)**

```bash
# For zsh (default on macOS)
echo 'export DATABASE_URL="postgresql://localhost/analytics_db"' >> ~/.zshrc
source ~/.zshrc

# For bash
echo 'export DATABASE_URL="postgresql://localhost/analytics_db"' >> ~/.bash_profile
source ~/.bash_profile
```

**Option B: Create .env file (project-specific)**

```bash
# In your project folder
echo 'DATABASE_URL=postgresql://localhost/analytics_db' > .env
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

And add to your `server.py`:
```python
from dotenv import load_dotenv
load_dotenv()  # Load .env file
```

### Step 3: Install Python PostgreSQL Driver

```bash
cd /Users/aribafarheen/the-shift-landing-page
pip3 install psycopg2-binary
```

### Step 4: Initialize Database

```bash
python3 database_unified.py
```

You should see:
```
✅ PostgreSQL database initialized successfully!
📍 Connected to: postgresql://localhost/analytics_db
```

### Step 5: Test It Works

```bash
python3 -c "
import database_unified as database
from datetime import datetime

# Test insert
event_id = database.insert_analytics({
    'event': 'test',
    'timestamp': datetime.now().isoformat(),
    'visitorId': 'test-local-123'
})
print(f'✅ PostgreSQL working! Event ID: {event_id}')

# Test query
stats = database.get_analytics_stats()
print(f'📊 Total events: {stats[\"total_events\"]}')
"
```

---

## Update Your Code to Use PostgreSQL

### 1. Update server.py

```python
# Change this line:
import database

# To this:
import database_unified as database
```

### 2. Update requirements.txt

Add:
```
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

### 3. Run Your Server

```bash
python3 run_local.py 5001
```

---

## Verify PostgreSQL is Running

```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Should show: postgresql@15 started

# Connect to database
psql analytics_db

# List tables
\dt

# Should show: analytics, registrations

# Exit
\q
```

---

## Common Issues & Solutions

### Issue: "createdb: command not found"

**Solution:** Add PostgreSQL to PATH
```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Issue: "psql: could not connect to server"

**Solution:** Start PostgreSQL service
```bash
brew services start postgresql@15
```

### Issue: "peer authentication failed"

**Solution:** Use socket connection
```bash
# Your DATABASE_URL should be:
export DATABASE_URL="postgresql://localhost/analytics_db"

# NOT:
# postgresql://username:password@localhost/analytics_db
```

### Issue: "psycopg2 import error"

**Solution:** Install binary version
```bash
pip3 install --upgrade psycopg2-binary
```

---

## Managing Your Local Database

### View Data

```bash
# Connect to database
psql analytics_db

# View registrations
SELECT * FROM registrations;

# View analytics
SELECT * FROM analytics LIMIT 10;

# Count records
SELECT COUNT(*) FROM analytics;
SELECT COUNT(*) FROM registrations;

# Exit
\q
```

### Backup Database

```bash
# Backup to file
pg_dump analytics_db > analytics_backup.sql

# Restore from backup
psql analytics_db < analytics_backup.sql
```

### Reset Database (if needed)

```bash
# Drop and recreate
dropdb analytics_db
createdb analytics_db
python3 database_unified.py  # Reinitialize tables
```

---

## Same Setup on Replit

### Step 1: Create PostgreSQL Database
1. Open your Repl
2. Click **Tools** → **Database** in sidebar
3. Click **"Create Database"**
4. Select **PostgreSQL**
5. Copy the connection string

### Step 2: Add to Secrets
1. Click **Secrets** (lock icon) in sidebar
2. Add new secret:
   - Key: `DATABASE_URL`
   - Value: `postgresql://...` (paste connection string)

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python3 database_unified.py
```

**That's it! Same code works on both!** 🎉

---

## Benefits of This Setup

✅ **Same Code Everywhere** - No platform-specific code  
✅ **Data Persists** - PostgreSQL saves data reliably  
✅ **Production Ready** - Same database as Replit  
✅ **Easy Testing** - Test locally before deploying  
✅ **Familiar Tools** - Use psql, pgAdmin, etc.  
✅ **Scalable** - PostgreSQL handles growth  

---

## Quick Commands Reference

```bash
# Install PostgreSQL
brew install postgresql@15

# Start/Stop Service
brew services start postgresql@15
brew services stop postgresql@15

# Create Database
createdb analytics_db

# Connect
psql analytics_db

# List Databases
psql -l

# Set Environment Variable
export DATABASE_URL="postgresql://localhost/analytics_db"

# Test Python Connection
python3 database_unified.py

# Run Server
python3 run_local.py 5001
```

---

## What to Do Next

1. ✅ Install PostgreSQL on Mac (Option 1 recommended)
2. ✅ Create `analytics_db` database
3. ✅ Set `DATABASE_URL` environment variable
4. ✅ Run `pip3 install psycopg2-binary`
5. ✅ Update `server.py` to import `database_unified`
6. ✅ Run `python3 database_unified.py` to init tables
7. ✅ Test with `python3 run_local.py 5001`
8. ✅ On Replit: Create PostgreSQL DB and add to Secrets
9. ✅ Deploy and verify data persists!

---

**Ready to get started? Run these commands:**

```bash
# Install PostgreSQL
brew install postgresql@15

# Start it
brew services start postgresql@15

# Create database
createdb analytics_db

# Set environment variable
echo 'export DATABASE_URL="postgresql://localhost/analytics_db"' >> ~/.zshrc
source ~/.zshrc

# Install Python driver
pip3 install psycopg2-binary

# Initialize database
python3 database_unified.py

# You're done! 🎉
```
