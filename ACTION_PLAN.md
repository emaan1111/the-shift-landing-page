# ✅ Action Plan - PostgreSQL Migration

## 🎯 Goal
Replace SQLite with PostgreSQL on both your Mac and Replit so data persists reliably.

---

## 📋 Steps to Complete TODAY

### Part 1: Local Mac Setup (10 minutes)

#### Step 1: Install PostgreSQL
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Step 2: Create Database
```bash
createdb analytics_db
```

#### Step 3: Set Environment Variable
```bash
echo 'export DATABASE_URL="postgresql://localhost/analytics_db"' >> ~/.zshrc
source ~/.zshrc
```

#### Step 4: Install Python Driver
```bash
cd /Users/aribafarheen/the-shift-landing-page
pip3 install psycopg2-binary
```

#### Step 5: Initialize Database
```bash
python3 database_unified.py
```

Expected output:
```
✅ PostgreSQL database initialized successfully!
📍 Connected to: postgresql://localhost/analytics_db
```

#### Step 6: Update server.py
Open `server.py` and change line 7:
```python
# Change this:
import database

# To this:
import database_unified as database
```

#### Step 7: Test Locally
```bash
python3 run_local.py 5001
```

Open browser: http://localhost:5001

Try registering - data should save to PostgreSQL!

---

### Part 2: Replit Setup (5 minutes)

#### Step 1: Create PostgreSQL Database on Replit
1. Open your Replit project
2. Click **"Tools"** in left sidebar
3. Click **"Database"**
4. Click **"Create Database"**
5. Select **"PostgreSQL"**
6. **Copy the connection string** (looks like: `postgresql://username:password@host:port/database`)

#### Step 2: Add DATABASE_URL to Secrets
1. Click **Secrets** (lock icon) in left sidebar
2. Click **"+ New Secret"**
3. Key: `DATABASE_URL`
4. Value: Paste the PostgreSQL connection string from Step 1
5. Click **"Add Secret"**

#### Step 3: Pull Latest Code
In Replit Shell:
```bash
git pull origin main
```

#### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 5: Update server.py on Replit
Same as local - change line 7:
```python
import database_unified as database
```

#### Step 6: Initialize Database
```bash
python3 database_unified.py
```

Expected output:
```
✅ PostgreSQL database initialized successfully!
📍 Connected to: postgresql://...
```

#### Step 7: Start Server
```bash
python3 server.py
```

Or just click the **"Run"** button!

#### Step 8: TEST DATA PERSISTENCE ⭐
1. Visit your live Replit URL
2. Register with a test email
3. **Stop the Repl** (click Stop button)
4. **Start the Repl again**
5. Check if the registration is still there
6. ✅ If yes = SUCCESS! Data persists!

---

## 🧪 Verification Tests

### Test 1: Analytics Tracking
```bash
python3 -c "
import database_unified as database
from datetime import datetime

event_id = database.insert_analytics({
    'event': 'test_event',
    'timestamp': datetime.now().isoformat(),
    'visitorId': 'test-123',
    'page': '/test'
})
print(f'✅ Event saved! ID: {event_id}')
"
```

### Test 2: Registration
```bash
python3 -c "
import database_unified as database
from datetime import datetime

reg_id = database.insert_registration({
    'email': 'test@example.com',
    'firstName': 'Test',
    'lastName': 'User',
    'timestamp': datetime.now().isoformat()
})
print(f'✅ Registration saved! ID: {reg_id}')
"
```

### Test 3: Referral Tracking
```bash
python3 test_referral_tracking.py
```

All tests should pass!

---

## 📝 Changes Made

### Files Created:
- ✅ `database_unified.py` - PostgreSQL database module (works everywhere)
- ✅ `POSTGRESQL_LOCAL_SETUP.md` - Mac setup guide
- ✅ `POSTGRESQL_MIGRATION.md` - Migration info
- ✅ `ACTION_PLAN.md` - This file

### Files to Update:
- 📝 `server.py` - Change import to `database_unified`

### Files to Keep (for now):
- 📦 `database.py` - Old SQLite (keep as backup until migration complete)
- 📦 `analytics.db` - Old SQLite database (can delete after)

### Files Already Updated:
- ✅ `requirements.txt` - Has `psycopg2-binary`
- ✅ `test_referral_tracking.py` - Already compatible
- ✅ `DATABASE_SETUP.md` - Updated with new info

---

## 🎯 Success Criteria

### Local (Mac):
- [x] PostgreSQL installed and running
- [x] `analytics_db` created
- [x] `DATABASE_URL` environment variable set
- [ ] `server.py` updated to use `database_unified`
- [ ] Server runs on port 5001
- [ ] Can register and data saves
- [ ] Can view analytics page with data

### Replit:
- [ ] PostgreSQL database created
- [ ] `DATABASE_URL` in Secrets
- [ ] Code pulled from GitHub
- [ ] Dependencies installed
- [ ] `server.py` updated
- [ ] Tables initialized
- [ ] Server runs without errors
- [ ] **Data persists after restart** ⭐ MOST IMPORTANT

---

## ⚠️ Important Notes

### Environment Variable Format:
```
# Local Mac:
postgresql://localhost/analytics_db

# Replit (example):
postgresql://username:password@db.host.com:5432/database_name
```

### Testing Data Persistence:
1. Add some data (register, visit pages)
2. **Stop the server/Repl completely**
3. **Start it again**
4. Check if data is still there
5. If yes ✅ = Working!
6. If no ❌ = Check DATABASE_URL is set correctly

### Troubleshooting:
- Can't connect to PostgreSQL locally? → Run `brew services start postgresql@15`
- Import error? → Run `pip3 install psycopg2-binary`
- Environment variable not working? → Run `source ~/.zshrc`
- Replit database empty? → Make sure DATABASE_URL is in Secrets, not just environment

---

## 🚀 After Migration

### What You Get:
✅ **Reliable data storage** - No more data loss  
✅ **Same system everywhere** - Local and Replit identical  
✅ **Production ready** - PostgreSQL is industry standard  
✅ **Easy debugging** - Use `psql` to inspect data  
✅ **Scalable** - Handles thousands of users  
✅ **Referrals work** - All tracking features functional  

### Clean Up (After Everything Works):
```bash
# On Mac
rm analytics.db
rm database.py
rm database_pg.py

# Keep database_unified.py - that's your main one now!
```

---

## 📞 Quick Help

### Check PostgreSQL is Running:
```bash
brew services list | grep postgresql
# Should show: postgresql@15 started
```

### Connect to Database:
```bash
psql analytics_db
# Inside psql:
\dt           # List tables
\d analytics  # Describe table
SELECT COUNT(*) FROM registrations;
\q            # Quit
```

### Check Environment Variable:
```bash
echo $DATABASE_URL
# Should show: postgresql://localhost/analytics_db
```

### View Database Data:
```bash
psql analytics_db -c "SELECT * FROM registrations;"
```

---

## ⏱️ Time Estimate

- **Local Setup**: 10 minutes
- **Replit Setup**: 5 minutes
- **Testing**: 5 minutes
- **Total**: ~20 minutes

**You'll be done in under 30 minutes!** 🎉

---

## 🎓 What You're Learning

By doing this, you're learning:
- How to install and use PostgreSQL
- Environment variables and configuration
- Database migrations
- The difference between SQLite (file-based) and PostgreSQL (server-based)
- Why production apps use PostgreSQL
- How to make code work on multiple platforms

These are valuable skills for any web developer!

---

## ✅ Final Checklist

**Before you start:**
- [ ] Read this whole document
- [ ] Have terminal open
- [ ] Have VS Code open
- [ ] Have Replit tab open

**During setup:**
- [ ] Follow each step carefully
- [ ] Check for success messages
- [ ] Test after each major step
- [ ] Don't skip the verification tests

**When done:**
- [ ] Local server works
- [ ] Replit server works
- [ ] Data persists after Repl restart
- [ ] All tests pass
- [ ] Referral tracking works
- [ ] You can view analytics dashboard

---

## 🎉 You're Ready!

Everything is prepared. All the code is written. The guides are complete.

**Just follow the steps above and you'll have a bulletproof database setup!**

Start here:
```bash
brew install postgresql@15
```

Let's go! 🚀
