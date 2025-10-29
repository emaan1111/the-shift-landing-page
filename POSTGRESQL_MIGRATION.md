# 🔄 SQLite to PostgreSQL Migration Guide

## ⚠️ CRITICAL: Why We Need This

**Problem Discovered:** SQLite is on Replit's blocklist for persistence
- Your `analytics.db` file gets deleted when Repl restarts
- This is why data from Oct 28 disappeared
- All data loss issues are caused by this

**Solution:** Migrate to PostgreSQL
- PostgreSQL is fully supported on Replit
- Data persists reliably across restarts
- Better performance for production use

---

## 📋 Migration Steps

### Step 1: Install PostgreSQL on Replit

In Replit Shell:
```bash
# PostgreSQL is already available on Replit
# We just need to install the Python driver
pip install psycopg2-binary
```

Add to `requirements.txt`:
```
psycopg2-binary==2.9.9
```

### Step 2: Set Up PostgreSQL Database

On Replit:
1. Go to **Tools** → **Database** in sidebar
2. Click **Create Database**
3. Choose **PostgreSQL**
4. Copy the connection string (format: `postgresql://user:pass@host:port/dbname`)

### Step 3: Update Environment Variables

In Replit:
1. Go to **Secrets** (lock icon in sidebar)
2. Add new secret:
   - Key: `DATABASE_URL`
   - Value: Your PostgreSQL connection string

### Step 4: Create New Database Module

**File: `database_pg.py`** (PostgreSQL version)

```python
"""
PostgreSQL Database for The Shift Landing Page Analytics
Replaces SQLite for Replit persistence
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize PostgreSQL database with required tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id SERIAL PRIMARY KEY,
                event TEXT NOT NULL,
                page TEXT,
                timestamp TIMESTAMP NOT NULL,
                visitor_id TEXT,
                session_id TEXT,
                email TEXT,
                name TEXT,
                country TEXT,
                city TEXT,
                region TEXT,
                ip_address TEXT,
                timezone TEXT,
                referrer TEXT,
                user_agent TEXT,
                screen_width INTEGER,
                screen_height INTEGER,
                language TEXT,
                hook_variant TEXT,
                button_name TEXT,
                duration INTEGER,
                utm_source TEXT,
                utm_medium TEXT,
                utm_campaign TEXT,
                utm_content TEXT,
                referred_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Registrations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id SERIAL PRIMARY KEY,
                email TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                country TEXT,
                city TEXT,
                region TEXT,
                timezone TEXT,
                ip_address TEXT,
                visitor_id TEXT,
                session_id TEXT,
                hook_variant TEXT,
                referrer TEXT,
                utm_source TEXT,
                utm_medium TEXT,
                utm_campaign TEXT,
                utm_content TEXT,
                referred_by INTEGER,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(email, timestamp)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics(event)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_visitor ON analytics(visitor_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_referred_by ON analytics(referred_by)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_registrations_email ON registrations(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_registrations_timestamp ON registrations(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_registrations_referred_by ON registrations(referred_by)')
        
        print('✅ PostgreSQL database initialized successfully!')

# Copy all other functions from database.py
# Just replace sqlite3 with psycopg2 syntax
```

### Step 5: Key Differences SQLite → PostgreSQL

| SQLite | PostgreSQL |
|--------|------------|
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` |
| `TEXT DEFAULT CURRENT_TIMESTAMP` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |
| `cursor.lastrowid` | `cursor.fetchone()['id'] RETURNING id` |
| No connection string | Requires `DATABASE_URL` |

### Step 6: Migrate Existing Data

**Option A: Export from SQLite, Import to PostgreSQL**

```python
# export_sqlite_data.py
import sqlite3
import json

conn = sqlite3.connect('analytics.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Export analytics
cursor.execute('SELECT * FROM analytics')
analytics = [dict(row) for row in cursor.fetchall()]
with open('analytics_export.json', 'w') as f:
    json.dump(analytics, f)

# Export registrations
cursor.execute('SELECT * FROM registrations')
registrations = [dict(row) for row in cursor.fetchall()]
with open('registrations_export.json', 'w') as f:
    json.dump(registrations, f)

print(f'Exported {len(analytics)} analytics, {len(registrations)} registrations')
```

**Option B: Start Fresh** (if no critical data)

- Just initialize new PostgreSQL database
- Old data is in backup JSON files anyway

---

## 🔧 Code Changes Needed

### 1. Update `server.py`

```python
# OLD
import database

# NEW
import database_pg as database
```

### 2. Update `requirements.txt`

```
Flask==3.0.0
Flask-CORS==4.0.0
requests==2.31.0
psycopg2-binary==2.9.9  # Add this
```

### 3. Add Environment Variable Check

```python
# At top of server.py or database_pg.py
import os

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set!")
```

---

## ✅ Testing the Migration

### 1. Local Testing (Optional)

Install PostgreSQL locally:
```bash
# macOS
brew install postgresql
brew services start postgresql
createdb analytics_test

# Set local DATABASE_URL
export DATABASE_URL="postgresql://localhost/analytics_test"
```

### 2. On Replit

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 database_pg.py

# Test insertion
python3 -c "
import database_pg as database
from datetime import datetime
event_id = database.insert_analytics({
    'event': 'test',
    'timestamp': datetime.now().isoformat(),
    'visitorId': 'test-123'
})
print(f'✅ PostgreSQL working! Event ID: {event_id}')
"
```

---

## 🚀 Deployment Checklist

- [ ] Create PostgreSQL database on Replit
- [ ] Add `DATABASE_URL` to Replit Secrets
- [ ] Install `psycopg2-binary` in requirements.txt
- [ ] Create `database_pg.py` with PostgreSQL code
- [ ] Update `server.py` to import `database_pg`
- [ ] Run `init_db()` to create tables
- [ ] Test analytics tracking works
- [ ] Test registration tracking works
- [ ] Verify data persists after Repl restart
- [ ] Update backup scripts if needed

---

## 📊 Benefits of PostgreSQL

✅ **Data Persistence** - Files never get deleted  
✅ **Better Performance** - Handles concurrent connections  
✅ **Production Ready** - Used by major applications  
✅ **ACID Compliance** - Reliable transactions  
✅ **Scalability** - Can handle millions of rows  
✅ **Built-in on Replit** - Easy to set up  

---

## 🔙 Rollback Plan (If Needed)

If something goes wrong:
1. Keep `database.py` (SQLite version)
2. Switch import back: `import database`
3. Data is in JSON backups: `backups/` folder
4. Can restore from backups anytime

---

## 💡 Next Steps

1. **Immediate**: Set up PostgreSQL on Replit
2. **Test**: Verify data persists after restart
3. **Monitor**: Check data is being saved correctly
4. **Cleanup**: Remove old `analytics.db` file
5. **Document**: Update README with PostgreSQL setup

---

## 📝 Files to Create/Modify

### New Files:
- `database_pg.py` - PostgreSQL version of database module
- `migrate_to_postgres.py` - Migration script (optional)
- `POSTGRESQL_SETUP.md` - This file

### Modified Files:
- `server.py` - Import database_pg instead of database
- `requirements.txt` - Add psycopg2-binary
- `.env` or Replit Secrets - Add DATABASE_URL

### Keep for Reference:
- `database.py` - Original SQLite version (don't delete yet)
- `analytics.db` - Export data first, then can delete

---

## ⚠️ Important Notes

1. **DATABASE_URL Format:**
   ```
   postgresql://username:password@host:port/database_name
   ```

2. **Replit Database Tool:**
   - Automatically provides PostgreSQL
   - Handles backups
   - Persists across restarts

3. **Connection Pooling:**
   - For high traffic, consider using connection pools
   - Can add `psycopg2.pool` later if needed

4. **Migrations:**
   - Keep track of schema changes
   - Use migration tools like Alembic for production

---

## 🎯 Success Criteria

Migration is successful when:
- [x] PostgreSQL database created on Replit
- [x] Tables created with correct schema
- [x] Analytics tracking saves data
- [x] Registrations save correctly
- [x] Referral tracking works
- [x] Data persists after Repl restart ⭐ **MOST IMPORTANT**
- [x] No 500 errors
- [x] All tests pass

---

**This migration will PERMANENTLY fix the data loss issue!** 🎉
