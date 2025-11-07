#!/usr/bin/env python3
"""
Backup PostgreSQL database to SQLite file
This script exports data from PostgreSQL and stores it in a SQLite backup file
"""

import os
import sys
from datetime import datetime
import sqlite3

# Import PostgreSQL database module
try:
    if not os.getenv('DATABASE_URL'):
        print("❌ ERROR: DATABASE_URL environment variable is not set!")
        print("Please set DATABASE_URL to your PostgreSQL connection string.")
        sys.exit(1)
    
    import database_unified as db_pg
    print("✅ Connected to PostgreSQL database")
except Exception as e:
    print(f"❌ ERROR: Failed to connect to PostgreSQL: {e}")
    sys.exit(1)


def create_sqlite_backup():
    """Create SQLite backup of PostgreSQL data"""
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'database_backups/backup_{timestamp}.db'
    
    # Ensure backup directory exists
    os.makedirs('database_backups', exist_ok=True)
    
    # Remove existing file if it exists
    if os.path.exists(backup_file):
        os.remove(backup_file)
    
    print(f"📦 Creating SQLite backup: {backup_file}")
    
    # Connect to SQLite
    conn = sqlite3.connect(backup_file)
    cursor = conn.cursor()
    
    try:
        # Create tables in SQLite
        print("📋 Creating backup tables...")
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                page TEXT,
                button_text TEXT,
                button_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                referrer TEXT,
                city TEXT,
                country TEXT
            )
        ''')
        
        # Registrations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                referrer TEXT,
                ip_address TEXT,
                city TEXT,
                country TEXT
            )
        ''')
        
        # Waiting list table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waiting_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Zoom optins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zoom_optins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                optin_timestamp TEXT NOT NULL
            )
        ''')
        
        print("✅ Tables created")
        
        # Backup analytics data
        print("📊 Backing up analytics data...")
        analytics_data = db_pg.get_all_analytics()
        for row in analytics_data:
            cursor.execute('''
                INSERT INTO analytics 
                (timestamp, event_type, page, button_text, button_id, ip_address, 
                 user_agent, referrer, city, country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['timestamp'], row['event_type'], row.get('page'),
                row.get('button_text'), row.get('button_id'), row.get('ip_address'),
                row.get('user_agent'), row.get('referrer'), row.get('city'),
                row.get('country')
            ))
        print(f"✅ Backed up {len(analytics_data)} analytics records")
        
        # Backup registrations data
        print("📝 Backing up registrations data...")
        registrations_data = db_pg.get_all_registrations()
        for row in registrations_data:
            cursor.execute('''
                INSERT INTO registrations 
                (timestamp, name, email, phone, referrer, ip_address, city, country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['timestamp'], row['name'], row['email'], row.get('phone'),
                row.get('referrer'), row.get('ip_address'), row.get('city'),
                row.get('country')
            ))
        print(f"✅ Backed up {len(registrations_data)} registration records")
        
        # Backup waiting list data
        print("⏳ Backing up waiting list data...")
        waiting_list_data = db_pg.get_all_waitinglist()
        for row in waiting_list_data:
            cursor.execute('''
                INSERT INTO waiting_list (timestamp, name, email, phone)
                VALUES (?, ?, ?, ?)
            ''', (
                row['timestamp'], row['name'], row['email'], row.get('phone')
            ))
        print(f"✅ Backed up {len(waiting_list_data)} waiting list records")
        
        # Backup settings data
        print("⚙️  Backing up settings data...")
        settings_data = db_pg.get_all_settings()
        for row in settings_data:
            cursor.execute('''
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (
                row['key'], row['value'], row['updated_at']
            ))
        print(f"✅ Backed up {len(settings_data)} settings")
        
        # Backup zoom optins data
        print("🎥 Backing up zoom optins data...")
        zoom_optins_data = db_pg.get_all_zoom_optins()
        for row in zoom_optins_data:
            cursor.execute('''
                INSERT INTO zoom_optins (name, email, optin_timestamp)
                VALUES (?, ?, ?)
            ''', (
                row['name'], row['email'], row['optin_timestamp']
            ))
        print(f"✅ Backed up {len(zoom_optins_data)} zoom optin records")
        
        # Commit changes
        conn.commit()
        
        # Get file size
        file_size = os.path.getsize(backup_file)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"\n✅ Backup completed successfully!")
        print(f"📁 File: {backup_file}")
        print(f"💾 Size: {file_size_mb:.2f} MB")
        
        # Also create a "latest" backup
        latest_backup = 'database_backups/backup_latest.db'
        import shutil
        shutil.copy2(backup_file, latest_backup)
        print(f"📁 Latest backup: {latest_backup}")
        
    except Exception as e:
        print(f"❌ ERROR during backup: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("PostgreSQL to SQLite Backup Tool")
    print("=" * 60)
    create_sqlite_backup()
    print("=" * 60)
