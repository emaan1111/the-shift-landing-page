# 🎯 Database Setup Summary - PostgreSQL Everywhere

## What We're Doing

**OLD Setup:**
- ❌ SQLite locally (analytics.db)
- ❌ SQLite on Replit → Data gets deleted!
- ❌ Different systems = confusion

**NEW Setup:**
- ✅ PostgreSQL locally
- ✅ PostgreSQL on Replit
- ✅ Same code everywhere
- ✅ Data persists reliably

---

# 🗄️ Database Setup Guide

This guide explains how to migrate from GitHub-based tracking to a database-based tracking system.

## Why Database?

✅ **Faster**: No GitHub API rate limits  
✅ **Simpler**: No need for GitHub tokens  
✅ **More reliable**: Direct storage, no network delays  
✅ **Easier queries**: SQL database for analytics  
✅ **Automatic deduplication**: Built-in unique constraints  

## What's Included

- **SQLite Database**: Simple, file-based database (no separate server needed)
- **Flask API Endpoints**: RESTful API for tracking
- **New JavaScript Tracker**: `tracker-db.js` replaces `tracker.js`
- **Migration Script**: Moves existing data from GitHub/backups to database

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python database.py
```

This creates `analytics.db` with two tables:
- `analytics` - Page visits, button clicks, and all events
- `registrations` - Registration data

### 3. Migrate Existing Data (Optional)

```bash
python migrate_to_database.py
```

This will:
- Import all data from `backups/` JSON files
- Import all data from GitHub analytics files
- Automatically skip duplicates

### 4. Update Your HTML Files

Replace the old tracker with the new one:

**Old:**
```html
<script src="js/tracker.js"></script>
```

**New:**
```html
<script src="js/tracker-db.js"></script>
```

Do this for all your HTML files:
- `index.html`
- `thank-you.html`
- `upsell.html`
- Any other pages using tracking

### 5. Restart Your Server

```bash
python server.py
```

## New API Endpoints

### Track Analytics Event
```
POST /api/analytics/track
Body: { event, page, visitorId, sessionId, ... }
```

### Track Registration
```
POST /api/analytics/registration
Body: { email, firstName, lastName, country, ... }
```

### Get All Registrations
```
GET /api/registrations
Returns: Array of registration objects
```

### Get Analytics Stats
```
GET /api/analytics/stats
Returns: { total_visits, unique_visitors, registrations_by_country, ... }
```

### Get Analytics Events
```
GET /api/analytics/events?event=page_visit&limit=100
Returns: Array of analytics events
```

## Database Schema

### Analytics Table
```sql
- id: Primary key
- event: 'page_visit', 'page_exit', 'button_click', etc.
- page: URL path
- timestamp: ISO 8601 timestamp
- visitor_id: Persistent visitor identifier
- session_id: Unique session identifier
- email, name, country, city, region
- ip_address, timezone
- referrer, user_agent
- screen_width, screen_height, language
- hook_variant: A/B test variant
- button_name: For click events
- duration: For exit events (seconds)
- utm_source, utm_medium, utm_campaign, utm_content
```

### Registrations Table
```sql
- id: Primary key
- email: UNIQUE with timestamp
- first_name, last_name, phone
- country, city, region, timezone
- ip_address
- visitor_id, session_id
- hook_variant
- referrer
- utm_source, utm_medium, utm_campaign, utm_content
- timestamp: ISO 8601 timestamp
```

## Advantages Over GitHub

| Feature | GitHub | Database |
|---------|--------|----------|
| Speed | Slow (API calls) | Fast (local) |
| Rate limits | Yes (5000/hour) | No |
| Setup complexity | High (tokens, permissions) | Low |
| Query capability | Limited (JSON files) | Full SQL |
| Real-time analytics | No | Yes |
| Backup | Automatic (Git) | Manual (file copy) |

## Backup Your Database

The database file is `analytics.db`. To backup:

```bash
# Simple backup
cp analytics.db analytics.db.backup

# With timestamp
cp analytics.db "analytics-$(date +%Y%m%d).db"
```

You can also export to JSON:

```bash
python -c "
import json
from database import get_all_registrations, get_all_analytics
with open('export-registrations.json', 'w') as f:
    json.dump(get_all_registrations(), f, indent=2)
with open('export-analytics.json', 'w') as f:
    json.dump(get_all_analytics(), f, indent=2)
"
```

## Viewing the Database

Use any SQLite browser:
- [DB Browser for SQLite](https://sqlitebrowser.org/) (Free, cross-platform)
- [SQLite Viewer](https://inloop.github.io/sqlite-viewer/) (Online)
- Command line: `sqlite3 analytics.db`

## Troubleshooting

### Database locked error
- Make sure only one Flask instance is running
- Close any SQLite browser applications

### Migration fails
- Check that your GitHub token is valid in `js/analytics-config.js`
- Check that backup files exist in `backups/` directory
- Run migration with verbose logging

### No data appearing
- Check browser console for JavaScript errors
- Verify Flask server is running on port 3000
- Check that `tracker-db.js` is loaded in your HTML

## Going Back to GitHub

If you want to revert:
1. Change HTML files back to `<script src="js/tracker.js"></script>`
2. Your GitHub data is still intact
3. Keep the database as a backup

## Questions?

- Database file: `analytics.db`
- Server logs: Check terminal where `python server.py` is running
- Browser logs: Open DevTools Console (F12)
