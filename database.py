"""
Database setup and models for The Shift Landing Page Analytics
Uses SQLite for simplicity - no separate database server needed
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

DB_FILE = 'analytics.db'

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
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
        
        # Page visits and events table
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
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(email, timestamp)
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics(event)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_visitor ON analytics(visitor_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_page ON analytics(page)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_registrations_email ON registrations(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_registrations_timestamp ON registrations(timestamp)')
        
        print('✅ Database initialized successfully!')

def insert_analytics(data):
    """Insert analytics event into database"""
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
        event_id = cursor.lastrowid
        
        # Auto-backup every 100 events
        if event_id % 100 == 0:
            auto_backup()
        
        return event_id

def insert_registration(data):
    """Insert registration into database"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO registrations (
                    email, first_name, last_name, phone,
                    country, city, region, timezone, ip_address,
                    visitor_id, session_id, hook_variant, referrer,
                    utm_source, utm_medium, utm_campaign, utm_content,
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
            # Duplicate registration (same email + timestamp)
            print(f'⚠️  Duplicate registration skipped: {data.get("email")}')
            return None

def get_all_analytics(event_type=None, start_date=None, end_date=None, limit=None):
    """Get analytics data with optional filtering"""
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

def get_all_registrations(limit=None):
    """Get all registrations"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = 'SELECT * FROM registrations ORDER BY timestamp DESC'
        
        if limit:
            query += ' LIMIT ?'
            cursor.execute(query, (limit,))
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_analytics_stats():
    """Get analytics statistics"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        stats = {}
        
        # Total visits
        cursor.execute("SELECT COUNT(*) as count FROM analytics WHERE event = 'page_visit'")
        stats['total_visits'] = cursor.fetchone()['count']
        
        # Unique visitors
        cursor.execute("SELECT COUNT(DISTINCT visitor_id) as count FROM analytics")
        stats['unique_visitors'] = cursor.fetchone()['count']
        
        # Total registrations
        cursor.execute("SELECT COUNT(*) as count FROM registrations")
        stats['total_registrations'] = cursor.fetchone()['count']
        
        # Button clicks
        cursor.execute("SELECT COUNT(*) as count FROM analytics WHERE event = 'button_click'")
        stats['button_clicks'] = cursor.fetchone()['count']
        
        # Registrations by country
        cursor.execute("""
            SELECT country, COUNT(*) as count 
            FROM registrations 
            WHERE country IS NOT NULL AND country != ''
            GROUP BY country 
            ORDER BY count DESC
        """)
        stats['registrations_by_country'] = [dict(row) for row in cursor.fetchall()]
        
        # Page views by page
        cursor.execute("""
            SELECT page, COUNT(*) as count 
            FROM analytics 
            WHERE event = 'page_visit'
            GROUP BY page 
            ORDER BY count DESC
        """)
        stats['page_views'] = [dict(row) for row in cursor.fetchall()]
        
        return stats

def delete_analytics_event(event_id):
    """Delete a specific analytics event by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM analytics WHERE id = ?', (event_id,))
        return cursor.rowcount > 0

def delete_registration(registration_id):
    """Delete a specific registration by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM registrations WHERE id = ?', (registration_id,))
        return cursor.rowcount > 0

def get_registration_by_id(registration_id):
    """Get a specific registration by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM registrations WHERE id = ?', (registration_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_analytics_event_by_id(event_id):
    """Get a specific analytics event by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM analytics WHERE id = ?', (event_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def auto_backup():
    """Automatically backup database to JSON files"""
    import os
    
    backup_dir = 'database_backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Backup analytics
            cursor.execute('SELECT * FROM analytics')
            analytics_rows = cursor.fetchall()
            analytics_data = [dict(row) for row in analytics_rows]
            
            # Backup registrations
            cursor.execute('SELECT * FROM registrations')
            registrations_rows = cursor.fetchall()
            registrations_data = [dict(row) for row in registrations_rows]
            
            # Save to latest files
            import json
            with open(os.path.join(backup_dir, 'analytics_latest.json'), 'w') as f:
                json.dump(analytics_data, f, indent=2)
            
            with open(os.path.join(backup_dir, 'registrations_latest.json'), 'w') as f:
                json.dump(registrations_data, f, indent=2)
            
            print(f'🔄 Auto-backup: {len(analytics_data)} analytics, {len(registrations_data)} registrations')
    except Exception as e:
        print(f'⚠️ Auto-backup failed: {e}')

if __name__ == '__main__':
    # Initialize database when run directly
    init_db()
    print('✅ Database setup complete!')
