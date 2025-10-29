#!/usr/bin/env python3
"""
Test script to verify analytics tracking is working correctly on Replit
"""
import sys
import os

# Add the workspace directory to the path
sys.path.insert(0, '/home/runner/workspace')

import database
from datetime import datetime

def test_analytics_insertion():
    """Test inserting analytics events"""
    print("=" * 60)
    print("Testing Analytics Database Insertion")
    print("=" * 60)
    
    # Test 1: Valid page_visit event (matches what tracker-db.js sends)
    print("\n1️⃣ Testing valid page_visit event...")
    test_event = {
        'event': 'page_visit',  # <-- This is the required field!
        'page': '/',
        'timestamp': datetime.now().isoformat(),
        'visitorId': 'test-visitor-123',
        'sessionId': 'test-session-456',
        'referrer': 'https://google.com',
        'userAgent': 'Mozilla/5.0 Test Browser',
        'screenWidth': 1920,
        'screenHeight': 1080,
        'language': 'en-US'
    }
    
    try:
        event_id = database.insert_analytics(test_event)
        print(f"   ✅ Success! Event ID: {event_id}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Button click event
    print("\n2️⃣ Testing button_click event...")
    button_event = {
        'event': 'button_click',
        'page': '/',
        'timestamp': datetime.now().isoformat(),
        'visitorId': 'test-visitor-123',
        'sessionId': 'test-session-456',
        'buttonName': 'Get Early Access'
    }
    
    try:
        event_id = database.insert_analytics(button_event)
        print(f"   ✅ Success! Event ID: {event_id}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Verify data was saved
    print("\n3️⃣ Verifying events were saved...")
    try:
        with database.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM analytics WHERE visitor_id = ?', ('test-visitor-123',))
            count = cursor.fetchone()[0]
            print(f"   ✅ Found {count} test events in database")
            
            # Show the events
            cursor.execute('''
                SELECT id, event, page, timestamp 
                FROM analytics 
                WHERE visitor_id = ? 
                ORDER BY id DESC 
                LIMIT 2
            ''', ('test-visitor-123',))
            
            events = cursor.fetchall()
            for row in events:
                print(f"      - ID {row[0]}: {row[1]} on {row[2]} at {row[3]}")
                
    except Exception as e:
        print(f"   ❌ Error reading database: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Analytics tracking is working!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_analytics_insertion()
    sys.exit(0 if success else 1)
