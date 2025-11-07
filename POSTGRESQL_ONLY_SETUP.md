# PostgreSQL Setup Complete ✅

## Changes Made

### 1. Removed SQLite Fallback
- Updated `server.py` to use PostgreSQL ONLY
- No more SQLite fallback - server will exit if DATABASE_URL is not set
- Added proper error messages and validation

### 2. SQLite Now Used ONLY for Backups
- Created `backup_to_sqlite.py` script
- Exports all PostgreSQL data to timestamped SQLite files
- Stores backups in `database_backups/` folder
- Creates both timestamped and "latest" backup files

### 3. Server Configuration
- Changed default port from 5000 to 5001 (port 5000 is used by AirPlay Receiver)
- Server can be started with: `python3 server.py`
- Or with custom port: `PORT=8000 python3 server.py`

### 4. Fixed Event Dashboard
- Fixed JavaScript syntax error in `loadSettings()` function (duplicate code removed)
- Added `showNotification()` helper function to `analytics.html`

## Current Setup

### Database
- **Type**: PostgreSQL 15.14
- **Database Name**: `analytics`
- **Connection**: `postgresql://aribafarheen@localhost:5432/analytics`
- **Status**: ✅ Running

### Server
- **URL**: http://127.0.0.1:5001
- **Status**: ✅ Running
- **Debug Mode**: ON

### Event Dashboard
- **URL**: http://127.0.0.1:5001/event-dashboard.html
- **Status**: ✅ Working

### Analytics Dashboard
- **URL**: http://127.0.0.1:5001/analytics.html
- **Status**: ✅ Working

## How to Use

### Starting the Server
```bash
# Export DATABASE_URL (or add to .env file)
export DATABASE_URL='postgresql://aribafarheen@localhost:5432/analytics'

# Start server
python3 server.py
```

### Creating a Backup
```bash
# Export DATABASE_URL first
export DATABASE_URL='postgresql://aribafarheen@localhost:5432/analytics'

# Run backup script
python3 backup_to_sqlite.py
```

This will create:
- `database_backups/backup_YYYYMMDD_HHMMSS.db` (timestamped backup)
- `database_backups/backup_latest.db` (always the most recent)

### Updating Settings (Like Zoom Link)

1. Go to Analytics Dashboard: http://127.0.0.1:5001/analytics.html
2. Scroll to "Event Configuration" section
3. Update the Zoom Link field
4. Click "Save Zoom Link" button
5. You'll see a success notification ✅

### Testing the Zoom Popup

1. Go to Event Dashboard: http://127.0.0.1:5001/event-dashboard.html
2. Click "Join Zoom Session" button
3. Modal popup will appear asking for name and email
4. Fill in the form and click "Join Zoom Now"
5. Your details are saved to database and Zoom opens in new tab

## Troubleshooting

### Issue: Zoom link not saving or popup not opening

**Solution 1: Check if server is running**
```bash
curl http://127.0.0.1:5001/api/settings/zoom_link
```
Should return JSON with the zoom link.

**Solution 2: Check browser console**
- Open browser DevTools (F12 or Cmd+Option+I)
- Look for JavaScript errors in Console tab
- Check Network tab to see if API calls are succeeding

**Solution 3: Verify database connection**
```bash
psql -U aribafarheen -d analytics -c "SELECT key, value FROM settings WHERE key = 'zoom_link';"
```

**Solution 4: Clear browser cache**
- Hard refresh the page (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
- Or clear browser cache completely

### Issue: Port 5000 in use

**Solution**: The server now uses port 5001 by default. If you need a different port:
```bash
export PORT=8000
python3 server.py
```

### Issue: DATABASE_URL not set

**Solution**: Make sure `.env` file exists with:
```
DATABASE_URL=postgresql://aribafarheen@localhost:5432/analytics
```

Or export it manually:
```bash
export DATABASE_URL='postgresql://aribafarheen@localhost:5432/analytics'
```

## Next Steps

1. ✅ Update Zoom link in analytics dashboard
2. ✅ Test popup functionality on event dashboard
3. ✅ Set up other event links (Community, Questions Form)
4. ✅ Test offer settings
5. 📅 Schedule regular backups with cron or similar

## Files Modified

- `server.py` - Removed SQLite fallback, added PostgreSQL-only mode
- `event-dashboard.html` - Fixed JavaScript syntax error
- `analytics.html` - Added showNotification helper function
- `backup_to_sqlite.py` - Created/updated backup script
- `.env` - Contains DATABASE_URL (already existed)

## Files to Keep

- `database_unified.py` - PostgreSQL database module
- `database_sqlite.py` - Keep for reference/backups only
- `analytics.db` - Old SQLite database (can be archived)
