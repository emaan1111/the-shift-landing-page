"""
Automatic Database Backup Script
Exports analytics.db to JSON files for safe keeping
Run this daily via cron job or manually
"""

import sqlite3
import json
from datetime import datetime
import os

DB_FILE = 'analytics.db'
BACKUP_DIR = 'database_backups'

def backup_database():
    """Backup database to JSON files"""
    
    # Create backup directory if it doesn't exist
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f'📁 Created backup directory: {BACKUP_DIR}')
    
    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get current date for filename
    today = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Backup analytics table
    print('📊 Backing up analytics data...')
    cursor.execute('SELECT * FROM analytics')
    analytics_rows = cursor.fetchall()
    analytics_data = [dict(row) for row in analytics_rows]
    
    analytics_file = os.path.join(BACKUP_DIR, f'analytics_{timestamp}.json')
    with open(analytics_file, 'w') as f:
        json.dump(analytics_data, f, indent=2)
    print(f'✅ Analytics backed up: {len(analytics_data)} records → {analytics_file}')
    
    # Backup registrations table
    print('📝 Backing up registrations data...')
    cursor.execute('SELECT * FROM registrations')
    registrations_rows = cursor.fetchall()
    registrations_data = [dict(row) for row in registrations_rows]
    
    registrations_file = os.path.join(BACKUP_DIR, f'registrations_{timestamp}.json')
    with open(registrations_file, 'w') as f:
        json.dump(registrations_data, f, indent=2)
    print(f'✅ Registrations backed up: {len(registrations_data)} records → {registrations_file}')
    
    # Create a "latest" version for easy access
    latest_analytics = os.path.join(BACKUP_DIR, 'analytics_latest.json')
    with open(latest_analytics, 'w') as f:
        json.dump(analytics_data, f, indent=2)
    
    latest_registrations = os.path.join(BACKUP_DIR, 'registrations_latest.json')
    with open(latest_registrations, 'w') as f:
        json.dump(registrations_data, f, indent=2)
    
    print(f'\n✨ Backup complete!')
    print(f'   Analytics: {len(analytics_data)} records')
    print(f'   Registrations: {len(registrations_data)} records')
    print(f'   Location: {BACKUP_DIR}/')
    
    conn.close()
    
    return analytics_file, registrations_file

def restore_from_backup(backup_file=None):
    """Restore database from JSON backup"""
    
    if not backup_file:
        # Use latest backup
        backup_file = os.path.join(BACKUP_DIR, 'analytics_latest.json')
    
    if not os.path.exists(backup_file):
        print(f'❌ Backup file not found: {backup_file}')
        return False
    
    print(f'🔄 Restoring from: {backup_file}')
    
    # Determine if it's analytics or registrations
    is_analytics = 'analytics' in os.path.basename(backup_file)
    
    # Load data
    with open(backup_file, 'r') as f:
        data = json.load(f)
    
    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if is_analytics:
        # Restore analytics
        print(f'📊 Restoring {len(data)} analytics records...')
        for row in data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO analytics (
                        id, event, page, timestamp, visitor_id, session_id,
                        email, name, country, city, region, ip_address, timezone,
                        referrer, user_agent, screen_width, screen_height, language,
                        hook_variant, button_name, duration,
                        utm_source, utm_medium, utm_campaign, utm_content, referred_by, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('id'), row.get('event'), row.get('page'), row.get('timestamp'),
                    row.get('visitor_id'), row.get('session_id'), row.get('email'), row.get('name'),
                    row.get('country'), row.get('city'), row.get('region'), row.get('ip_address'),
                    row.get('timezone'), row.get('referrer'), row.get('user_agent'),
                    row.get('screen_width'), row.get('screen_height'), row.get('language'),
                    row.get('hook_variant'), row.get('button_name'), row.get('duration'),
                    row.get('utm_source'), row.get('utm_medium'), row.get('utm_campaign'),
                    row.get('utm_content'), row.get('referred_by'), row.get('created_at')
                ))
            except Exception as e:
                print(f'⚠️  Error restoring record {row.get("id")}: {e}')
    else:
        # Restore registrations
        print(f'📝 Restoring {len(data)} registration records...')
        for row in data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO registrations (
                        id, email, first_name, last_name, phone,
                        country, city, region, timezone, ip_address,
                        visitor_id, session_id, hook_variant, referrer,
                        utm_source, utm_medium, utm_campaign, utm_content,
                        referred_by, timestamp, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('id'), row.get('email'), row.get('first_name'), row.get('last_name'),
                    row.get('phone'), row.get('country'), row.get('city'), row.get('region'),
                    row.get('timezone'), row.get('ip_address'), row.get('visitor_id'),
                    row.get('session_id'), row.get('hook_variant'), row.get('referrer'),
                    row.get('utm_source'), row.get('utm_medium'), row.get('utm_campaign'),
                    row.get('utm_content'), row.get('referred_by'), row.get('timestamp'),
                    row.get('created_at')
                ))
            except Exception as e:
                print(f'⚠️  Error restoring record {row.get("id")}: {e}')
    
    conn.commit()
    conn.close()
    
    print(f'✅ Restore complete!')
    return True

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        # Restore mode
        backup_file = sys.argv[2] if len(sys.argv) > 2 else None
        restore_from_backup(backup_file)
    else:
        # Backup mode (default)
        backup_database()
