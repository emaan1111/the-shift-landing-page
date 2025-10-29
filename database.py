"""
Database setup and models for The Shift Landing Page Analytics
Uses PostgreSQL for production-grade data storage and scalability
"""

import psycopg2
import psycopg2.extras
import os
import json
from datetime import datetime
from contextlib import contextmanager

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
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
                event VARCHAR(100) NOT NULL,
                page VARCHAR(500),
                timestamp TIMESTAMPTZ NOT NULL,
                visitor_id VARCHAR(100),
                session_id VARCHAR(100),
                email VARCHAR(255),
                name VARCHAR(255),
                country VARCHAR(100),
                city VARCHAR(100),
                region VARCHAR(100),
                ip_address VARCHAR(50),
                timezone VARCHAR(100),
                referrer TEXT,
                user_agent TEXT,
                screen_width INTEGER,
                screen_height INTEGER,
                language VARCHAR(50),
                hook_variant VARCHAR(100),
                button_name VARCHAR(255),
                duration INTEGER,
                utm_source VARCHAR(255),
                utm_medium VARCHAR(255),
                utm_campaign VARCHAR(255),
                utm_content VARCHAR(255),
                referred_by VARCHAR(100),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Registrations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                phone VARCHAR(50),
                country VARCHAR(100),
                city VARCHAR(100),
                region VARCHAR(100),
                timezone VARCHAR(100),
                ip_address VARCHAR(50),
                visitor_id VARCHAR(100),
                session_id VARCHAR(100),
                hook_variant VARCHAR(100),
                referrer TEXT,
                utm_source VARCHAR(255),
                utm_medium VARCHAR(255),
                utm_campaign VARCHAR(255),
                utm_content VARCHAR(255),
                referred_by VARCHAR(100),
                timestamp TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
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
            event_id = cursor.fetchone()[0]
            
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
            return cursor.fetchone()[0]
        except psycopg2.IntegrityError:
            # Duplicate registration (same email + timestamp)
            print(f'⚠️  Duplicate registration skipped: {data.get("email")}')
            return None

def get_all_analytics(event_type=None, start_date=None, end_date=None, limit=None):
    """Get analytics data with optional filtering"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
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
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
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
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
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
        cursor.execute('DELETE FROM analytics WHERE id = %s', (event_id,))
        return cursor.rowcount > 0

def delete_registration(registration_id):
    """Delete a specific registration by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM registrations WHERE id = %s', (registration_id,))
        return cursor.rowcount > 0

def get_registration_by_id(registration_id):
    """Get a specific registration by ID"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM registrations WHERE id = %s', (registration_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_analytics_event_by_id(event_id):
    """Get a specific analytics event by ID"""
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM analytics WHERE id = %s', (event_id,))
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
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Backup analytics
            cursor.execute('SELECT * FROM analytics')
            analytics_rows = cursor.fetchall()
            analytics_data = [dict(row) for row in analytics_rows]
            
            # Backup registrations
            cursor.execute('SELECT * FROM registrations')
            registrations_rows = cursor.fetchall()
            registrations_data = [dict(row) for row in registrations_rows]
            
            # Convert datetime objects to strings for JSON serialization
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            # Process data for JSON serialization
            for item in analytics_data:
                for key, value in item.items():
                    item[key] = serialize_datetime(value)
            
            for item in registrations_data:
                for key, value in item.items():
                    item[key] = serialize_datetime(value)
            
            # Save to latest files
            with open(os.path.join(backup_dir, 'analytics_latest.json'), 'w') as f:
                json.dump(analytics_data, f, indent=2)
            
            with open(os.path.join(backup_dir, 'registrations_latest.json'), 'w') as f:
                json.dump(registrations_data, f, indent=2)
            
            print(f'🔄 Auto-backup: {len(analytics_data)} analytics, {len(registrations_data)} registrations')
    except Exception as e:
        print(f'⚠️ Auto-backup failed: {e}')

def get_referral_stats(registration_id=None):
    """Get referral statistics
    
    Args:
        registration_id: If provided, get stats for specific user. If None, get overall stats.
    
    Returns:
        Dictionary with referral statistics
    """
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        if registration_id:
            # Stats for a specific referrer
            cursor.execute('''
                SELECT COUNT(*) as referral_count
                FROM registrations
                WHERE referred_by = %s
            ''', (registration_id,))
            result = cursor.fetchone()
            referral_count = result['referral_count'] if result else 0
            
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
            result = cursor.fetchone()
            visit_count = result['visit_count'] if result else 0
            
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
            result = cursor.fetchone()
            total_referrals = result['total_referrals'] if result else 0
            
            cursor.execute('''
                SELECT COUNT(*) as total_visits
                FROM analytics
                WHERE referred_by IS NOT NULL
            ''')
            result = cursor.fetchone()
            total_visits = result['total_visits'] if result else 0
            
            return {
                'total_referrals': total_referrals,
                'total_visits': total_visits,
                'top_referrers': top_referrers
            }

if __name__ == '__main__':
    # Initialize database when run directly
    init_db()
    print('✅ Database setup complete!')
