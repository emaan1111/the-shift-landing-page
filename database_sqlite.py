"""
Simple SQLite database for local development
"""

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime

DB_FILE = 'analytics.db'

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize the database with required tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                page TEXT,
                timestamp TEXT NOT NULL,
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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Registrations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(email, timestamp)
            )
        ''')
        
        # Waiting list table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waiting_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                hear_about TEXT,
                page TEXT,
                user_agent TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Initialize default settings
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value)
            VALUES ('site_closed', 'false')
        ''')
        
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value)
            VALUES ('closed_message', 'Registration is currently closed. Join our waiting list to be notified when we open again!')
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics(event)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_registrations_email ON registrations(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_waitinglist_email ON waiting_list(email)')
        
        print('✅ SQLite database initialized successfully!')

def insert_analytics(data):
    """Insert analytics event"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analytics (
                event, page, timestamp, visitor_id, session_id,
                email, name, country, city, region, ip_address, timezone,
                referrer, user_agent, screen_width, screen_height, language,
                hook_variant, button_name, duration,
                utm_source, utm_medium, utm_campaign, utm_content, referred_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('event'),
            data.get('page'),
            data.get('timestamp'),
            data.get('visitorId'),
            data.get('sessionId'),
            data.get('email'),
            data.get('name'),
            data.get('country'),
            data.get('city'),
            data.get('region'),
            data.get('ipAddress'),
            data.get('timezone'),
            data.get('referrer'),
            data.get('userAgent'),
            data.get('screenWidth'),
            data.get('screenHeight'),
            data.get('language'),
            data.get('hookVariant'),
            data.get('buttonName'),
            data.get('duration'),
            data.get('utmSource'),
            data.get('utmMedium'),
            data.get('utmCampaign'),
            data.get('utmContent'),
            data.get('referredBy')
        ))
        return cursor.lastrowid

def insert_registration(data):
    """Insert registration"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO registrations (
                    email, first_name, last_name, phone, country, city, region,
                    timezone, ip_address, visitor_id, session_id, hook_variant,
                    referrer, utm_source, utm_medium, utm_campaign, utm_content,
                    referred_by, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('email'),
                data.get('firstName'),
                data.get('lastName'),
                data.get('phone'),
                data.get('country'),
                data.get('city'),
                data.get('region'),
                data.get('timezone'),
                data.get('ipAddress'),
                data.get('visitorId'),
                data.get('sessionId'),
                data.get('hookVariant'),
                data.get('referrer'),
                data.get('utmSource'),
                data.get('utmMedium'),
                data.get('utmCampaign'),
                data.get('utmContent'),
                data.get('referredBy'),
                data.get('timestamp')
            ))
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

def insert_waitinglist(data):
    """Insert waiting list entry"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO waiting_list (
                    email, first_name, last_name, phone, hear_about,
                    page, user_agent, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('email'),
                data.get('firstName'),
                data.get('lastName'),
                data.get('phone'),
                data.get('hearAbout'),
                data.get('page'),
                data.get('userAgent'),
                data.get('timestamp')
            ))
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

def get_all_registrations():
    """Get all registrations"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM registrations ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_all_analytics(event_type=None, start_date=None, end_date=None, limit=None):
    """Get analytics events with filtering"""
    with get_db() as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM analytics WHERE 1=1'
        params = []
        
        if event_type:
            query += ' AND event = ?'
            params.append(event_type)
        
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date)
        
        query += ' ORDER BY timestamp DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_all_waitinglist():
    """Get all waiting list entries"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM waiting_list ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_setting(key):
    """Get a setting value"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row['value'] if row else None

def set_setting(key, value):
    """Set a setting value"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, datetime('now'))
        ''', (key, value))
        return True

def get_all_settings():
    """Get all settings"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT key, value, updated_at FROM settings')
        rows = cursor.fetchall()
        return {row['key']: {'value': row['value'], 'updated_at': row['updated_at']} for row in rows}

def get_analytics_stats():
    """Get analytics statistics"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM analytics')
        analytics_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM registrations')
        registrations_count = cursor.fetchone()['count']
        
        return {
            'total_events': analytics_count,
            'total_registrations': registrations_count
        }

if __name__ == '__main__':
    init_db()
    print('✅ Database setup complete!')
