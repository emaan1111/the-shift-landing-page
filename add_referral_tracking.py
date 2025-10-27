"""
Add referral tracking columns to database
"""
import sqlite3

DB_FILE = 'analytics.db'

def add_referral_columns():
    """Add referred_by column to analytics and registrations tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists in analytics table
        cursor.execute("PRAGMA table_info(analytics)")
        analytics_columns = [col[1] for col in cursor.fetchall()]
        
        if 'referred_by' not in analytics_columns:
            cursor.execute('ALTER TABLE analytics ADD COLUMN referred_by INTEGER')
            print('✅ Added referred_by column to analytics table')
        else:
            print('ℹ️  referred_by column already exists in analytics table')
        
        # Check if column already exists in registrations table
        cursor.execute("PRAGMA table_info(registrations)")
        registrations_columns = [col[1] for col in cursor.fetchall()]
        
        if 'referred_by' not in registrations_columns:
            cursor.execute('ALTER TABLE registrations ADD COLUMN referred_by INTEGER')
            print('✅ Added referred_by column to registrations table')
        else:
            print('ℹ️  referred_by column already exists in registrations table')
        
        # Create index for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_referred_by ON analytics(referred_by)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_registrations_referred_by ON registrations(referred_by)')
        print('✅ Created indexes for referral tracking')
        
        conn.commit()
        print('✅ Referral tracking migration completed successfully!')
        
    except Exception as e:
        print(f'❌ Error during migration: {e}')
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    add_referral_columns()
