# Sync Database from Replit to Local

## Option 1: Download Database from Replit (Recommended)

### In Replit:
1. Open the Shell in Replit
2. Run this command to compress the database:
```bash
tar -czf analytics-backup.tar.gz analytics.db
```

3. The file will appear in your file explorer
4. Download `analytics-backup.tar.gz` to your local machine

### On Your Local Machine:
1. Extract and replace your local database:
```bash
cd /Users/aribafarheen/the-shift-landing-page
tar -xzf ~/Downloads/analytics-backup.tar.gz
```

2. Verify the data:
```bash
python3 -c "from database import get_all_analytics; print(f'Total events: {len(get_all_analytics())}')"
```

---

## Option 2: Temporarily Check In Database (Quick but not ideal)

### In Replit:
1. Temporarily remove analytics.db from .gitignore:
```bash
# Comment out the database lines in .gitignore
sed -i 's/^analytics.db/# analytics.db/' .gitignore
sed -i 's/^\*.db/# *.db/' .gitignore
```

2. Add and commit the database:
```bash
git add analytics.db
git commit -m "Temporary: Add database for sync"
git push origin main
```

### On Your Local Machine:
```bash
# Pull the database
git pull origin main

# Copy the database to a backup location
cp analytics.db analytics.db.from-replit

# Restore .gitignore to ignore database again
git pull origin main  # This should get the fixed .gitignore
```

### Back in Replit:
```bash
# Restore .gitignore
git checkout .gitignore
git add .gitignore
git commit -m "Restore .gitignore to ignore database"
git push origin main
```

---

## Option 3: Use Replit Database Export Feature

### In Replit:
1. Go to the "Database" tab in Replit (if available)
2. Export the database
3. Import on your local machine

---

## Recommended Approach:

**Option 1** is the safest and cleanest - just download the file directly from Replit without involving Git at all.
