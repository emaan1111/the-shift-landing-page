# Automatic Backup Setup for Replit

## Problem
Replit's ephemeral storage can lose data when containers restart. Analytics data might disappear after a period of inactivity.

## Solutions Implemented

### 1. Auto-Backup on Every 100 Events
The `database.py` now automatically backs up data every 100 analytics events to:
- `database_backups/analytics_latest.json`
- `database_backups/registrations_latest.json`

### 2. Manual Backup Command
Run anytime on Replit:
```bash
python3 backup_database.py
```

This creates timestamped backups in the `database_backups/` folder.

### 3. Scheduled Backups (Recommended)

**Option A: Using Replit's Always On + Cron (Requires Replit Hacker Plan)**

1. Install cron:
```bash
apt-get update && apt-get install -y cron
```

2. Create a cron job:
```bash
# Run backup every hour
echo "0 * * * * cd /home/runner/the-shift-landing-page && python3 backup_database.py >> /tmp/backup.log 2>&1" | crontab -
```

3. Start cron:
```bash
service cron start
```

**Option B: Using External Cron Service (Free)**

1. Sign up for a free cron service like:
   - https://cron-job.org
   - https://www.easycron.com

2. Create an endpoint in `server.py` for backups:
```python
@app.route('/api/backup/trigger', methods=['POST'])
def trigger_backup():
    # Add a secret key for security
    if request.headers.get('X-Backup-Secret') != 'your-secret-key-here':
        return jsonify({'error': 'Unauthorized'}), 401
    
    import backup_database
    backup_database.backup_database()
    return jsonify({'success': True, 'message': 'Backup completed'})
```

3. Set up the cron service to hit:
   `https://your-replit-url.repl.co/api/backup/trigger`
   with header: `X-Backup-Secret: your-secret-key-here`

**Option C: Download Backups Regularly to Your Local Machine**

1. On Replit, run:
```bash
python3 backup_database.py
```

2. Download the `database_backups` folder from Replit's file explorer

3. On your local machine, run:
```bash
./download_replit_database.sh
```

This restores your local database from the Replit backups.

### 4. Monitoring

Check if backups are working:
```bash
ls -lh database_backups/
```

View recent backup:
```bash
python3 -c "import json; data = json.load(open('database_backups/registrations_latest.json')); print(f'Registrations in backup: {len(data)}')"
```

## Restoration

If data is lost, restore from backup:

```bash
python3 backup_database.py restore database_backups/analytics_latest.json
python3 backup_database.py restore database_backups/registrations_latest.json
```

Or run the check script:
```bash
python3 check_today_registrations.py
```

## Best Practice

1. **Enable "Always On"** in Replit (requires Hacker plan) - prevents container from sleeping
2. **Run manual backups** before making any major changes
3. **Download backups** to your local machine regularly
4. **Monitor** the `database_backups/` folder to ensure backups are happening

## Current Status

✅ Auto-backup every 100 events: **ACTIVE**
✅ Manual backup script: **READY**
✅ Backup restoration script: **READY**
⏳ Scheduled backups: **NEEDS SETUP** (see options above)
