# Registration Backup System

## Overview
All registrations are now backed up in **three places** for maximum safety:

1. **ClickFunnels** (Primary) - Your CRM
2. **GitHub Analytics** (Cloud Backup) - Stored in `analytics/visits-YYYY-MM-DD.json` files with `event: "registration"`
3. **Local Server** (Local Backup) - Stored in `backups/registrations-YYYY-MM-DD.json` files

## How It Works

### Automatic Backups
When a user registers on the landing page:
1. Form data is sent to ClickFunnels API ✅
2. Registration data is backed up to GitHub analytics (via tracker.js) ✅
3. Registration data is saved to local JSON file (via Flask server) ✅

All three backups happen simultaneously. If one fails, the others still succeed.

### Backup Storage Locations

#### GitHub Analytics
- **Path**: `analytics/visits-YYYY-MM-DD.json`
- **Format**: JSON array with entries where `event: "registration"`
- **Retention**: Permanent (in your GitHub repo)
- **Access**: Via analytics dashboard or GitHub directly

#### Local Server Backups
- **Path**: `backups/registrations-YYYY-MM-DD.json`
- **Format**: JSON array organized by date
- **Retention**: Local only (not committed to Git)
- **Access**: Via `view-registrations.py` script or direct file access

## Viewing Backups

### View Local Backups
Run the Python script from your terminal:

```bash
python3 view-registrations.py
```

This will display all registrations in a formatted table with:
- Name
- Email
- Country
- City
- Timestamp

### View GitHub Backups
1. Open the analytics dashboard at `http://localhost:3000/analytics.html`
2. Filter "Recent Activity" by event type or search for registrations
3. Or view raw data files directly in your GitHub repo under `analytics/`

### Export Backups
To export all registrations to a CSV file:

```bash
# Coming soon - create export script if needed
```

## Data Fields Stored

Each registration backup includes:
```json
{
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "country": "United States",
  "city": "New York",
  "timestamp": "2025-10-25T10:30:00.000Z",
  "source": "Registration Form - The Shift Landing Page",
  "clickfunnelsSuccess": true
}
```

## Security & Privacy

⚠️ **Important**: The `backups/` directory contains personal information and is:
- **Excluded from Git** (via `.gitignore`)
- **Stored locally only** on your server
- **Not synchronized** to GitHub

**Recommendation**: 
- Back up the `backups/` directory regularly to a secure location
- Ensure proper file permissions (only you can read)
- Consider encrypting backups for sensitive data

## Troubleshooting

### No backups directory?
The directory is created automatically on first registration. If it doesn't exist, no registrations have been received yet.

### Missing registrations?
Check all three locations:
1. ClickFunnels dashboard
2. GitHub analytics files
3. Local `backups/` folder

If missing from all three, the registration likely failed to submit.

### Permission errors?
Ensure the Flask server has write permissions to the `backups/` directory:
```bash
chmod 755 backups/
```

## Manual Backup

To manually backup all registrations:

1. **Export from ClickFunnels**: Use ClickFunnels export feature
2. **Clone GitHub repo**: All analytics data is in version control
3. **Copy local files**: `cp -r backups/ backups-$(date +%Y%m%d)/`

## Recovery

If you need to recover registrations:
1. Check local `backups/` files first (fastest)
2. Check GitHub analytics files (reliable cloud backup)
3. Check ClickFunnels dashboard (primary source)
