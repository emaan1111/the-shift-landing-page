# Fix: Git Pull Error in Replit

If you're getting a fatal error when trying to pull code in Replit, it's because the `analytics.db` file is now in `.gitignore` but Replit still has the old tracked version.

## Quick Fix (Run in Replit Shell):

```bash
# Backup your current database (optional, but recommended)
cp analytics.db analytics.db.backup

# Remove the conflicting file
rm analytics.db

# Now pull the latest changes
git pull origin main

# Your database will be recreated automatically when you run the server
python server.py
```

## Alternative: Force Pull (if above doesn't work)

```bash
# Stash local changes
git stash

# Pull latest code
git pull origin main

# Restore your local changes (optional)
git stash pop
```

## What Changed?

- `analytics.db` is now in `.gitignore` to prevent database conflicts
- Each environment (local, Replit, production) will have its own database
- The database is automatically created when the server starts via `init_db()`
- Your analytics data will be fresh in each environment

## Note:

After pulling, if you want to keep your old data:
1. Restore from backup: `cp analytics.db.backup analytics.db`
2. Or migrate from GitHub analytics files: `python migrate_to_database.py`
