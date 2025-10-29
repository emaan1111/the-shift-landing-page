"""
Unified Database Module - Works on both Local and Replit
Automatically uses PostgreSQL with environment-based configuration
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager
from datetime import datetime

# Get database URL from environment variable
# Local: Set in .env file or export DATABASE_URL=...
# Replit: Set in Secrets (DATABASE_URL)
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("\n⚠️  WARNING: DATABASE_URL not set!")
    print("   Local: Create .env file with DATABASE_URL")
    print("   Replit: Add DATABASE_URL to Secrets")
    print("\n   Example: postgresql://user:password@localhost:5432/analytics")
    raise ValueError("DATABASE_URL environment variable is required")

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
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
                id SERIAL PRIMARY KEY,
                event TEXT NOT NULL,
                page TEXT,
                timestamp TIMESTAMP NOT NULL,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Registrations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id SERIAL PRIMARY KEY,
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
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(email, timestamp)
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics(event)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_visitor ON analytics(visitor_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_page ON analytics(page)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_referred_by ON analytics(referred_by)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_registrations_email ON registrations(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_registrations_timestamp ON registrations(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_registrations_referred_by ON registrations(referred_by)')
        
        print('✅ Database initialized successfully!')

def insert_analytics(data):
    """Insert analytics event into database"""
    # Validate required fields
    if not data.get('event'):
        raise ValueError(f"Missing required field 'event'. Received data: {list(data.keys())}")
    if not data.get('timestamp'):
        raise ValueError(f"Missing required field 'timestamp'. Received data: {list(data.keys())}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO analytics (
                    event, page, timestamp, visitor_id, session_id,
                    email, name, country, city, region, ip_address, timezone,
                    referrer, user_agent, screen_width, screen_height, language,
                    hook_variant, button_name, duration,
                    utm_source, utm_medium, utm_campaign, utm_content, referred_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
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
            event_id = cursor.fetchone()['id']
            
            # Auto-backup every 100 events
            if event_id % 100 == 0:
                auto_backup()
            
            return event_id
        except Exception as e:
            # Add more context to the error
            raise Exception(f"Database insertion failed: {e}. Data keys: {list(data.keys())}")

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
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
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
            return cursor.fetchone()['id']
        except psycopg2.IntegrityError:
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
            query += ' AND event = %s'
            params.append(event_type)
        
        if start_date:
            query += ' AND timestamp >= %s'
            params.append(start_date)
        
        if end_date:
            query += ' AND timestamp <= %s'
            params.append(end_date)
        
        query += ' ORDER BY timestamp DESC'
        
        if limit:
            query += ' LIMIT %s'
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
            query += ' LIMIT %s'
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
        
        # Total events
        cursor.execute('SELECT COUNT(*) as count FROM analytics')
        stats['total_events'] = cursor.fetchone()['count']
        
        # Events by type
        cursor.execute('SELECT event, COUNT(*) as count FROM analytics GROUP BY event')
        stats['events_by_type'] = [dict(row) for row in cursor.fetchall()]
        
        # Total registrations
        cursor.execute('SELECT COUNT(*) as count FROM registrations')
        stats['total_registrations'] = cursor.fetchone()['count']
        
        # Unique visitors
        cursor.execute('SELECT COUNT(DISTINCT visitor_id) as count FROM analytics WHERE visitor_id IS NOT NULL')
        stats['unique_visitors'] = cursor.fetchone()['count']
        
        return stats

def delete_analytics_event(event_id):
    """Delete an analytics event by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM analytics WHERE id = %s', (event_id,))
        return cursor.rowcount > 0

def delete_registration(registration_id):
    """Delete a registration by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM registrations WHERE id = %s', (registration_id,))
        return cursor.rowcount > 0

def get_registration_by_id(registration_id):
    """Get a specific registration by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM registrations WHERE id = %s', (registration_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_analytics_event_by_id(event_id):
    """Get a specific analytics event by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM analytics WHERE id = %s', (event_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_referral_stats(registration_id=None):
    """Get referral statistics
    
    Args:
        registration_id: If provided, get stats for specific user. If None, get overall stats.
    
    Returns:
        Dictionary with referral statistics
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        if registration_id:
            # Stats for a specific referrer
            cursor.execute('''
                SELECT COUNT(*) as referral_count
                FROM registrations
                WHERE referred_by = %s
            ''', (registration_id,))
            referral_count = cursor.fetchone()['referral_count']
            
            cursor.execute('''
                SELECT id, email, first_name, last_name, timestamp
                FROM registrations
                WHERE referred_by = %s
                ORDER BY timestamp DESC
            ''', (registration_id,))
            referrals = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT COUNT(*) as visit_count
                FROM analytics
                WHERE referred_by = %s
            ''', (registration_id,))
            visit_count = cursor.fetchone()['visit_count']
            
            return {
                'referrer_id': registration_id,
                'total_referrals': referral_count,
                'total_visits': visit_count,
                'referrals': referrals
            }
        else:
            # Overall referral stats
            cursor.execute('''
                SELECT 
                    referred_by,
                    COUNT(*) as referral_count
                FROM registrations
                WHERE referred_by IS NOT NULL
                GROUP BY referred_by
                ORDER BY referral_count DESC
            ''')
            top_referrers = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT COUNT(*) as total_referrals
                FROM registrations
                WHERE referred_by IS NOT NULL
            ''')
            total_referrals = cursor.fetchone()['total_referrals']
            
            cursor.execute('''
                SELECT COUNT(*) as total_visits
                FROM analytics
                WHERE referred_by IS NOT NULL
            ''')
            total_visits = cursor.fetchone()['total_visits']
            
            return {
                'total_referrals': total_referrals,
                'total_visits': total_visits,
                'top_referrers': top_referrers
            }

def auto_backup():
    """Automatically backup database to JSON files"""
    import os
    import json
    
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
            
            # Convert datetime objects to strings for JSON serialization
            for item in analytics_data:
                if 'timestamp' in item and item['timestamp']:
                    item['timestamp'] = item['timestamp'].isoformat()
                if 'created_at' in item and item['created_at']:
                    item['created_at'] = item['created_at'].isoformat()
            
            for item in registrations_data:
                if 'timestamp' in item and item['timestamp']:
                    item['timestamp'] = item['timestamp'].isoformat()
                if 'created_at' in item and item['created_at']:
                    item['created_at'] = item['created_at'].isoformat()
            
            # Save to latest files
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
