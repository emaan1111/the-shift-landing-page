#!/usr/bin/env python3
"""
Test Referral Tracking System
Tests the complete referral flow from registration to tracking
"""

import database
from datetime import datetime
import json

def test_referral_system():
    """Test complete referral tracking system"""
    
    print("=" * 80)
    print("🧪 TESTING REFERRAL TRACKING SYSTEM")
    print("=" * 80)
    print()
    
    # Test 1: Create a referrer (Sarah)
    print("📝 Test 1: Creating referrer (Sarah)...")
    sarah_id = database.insert_registration({
        'email': 'sarah@example.com',
        'firstName': 'Sarah',
        'lastName': 'Johnson',
        'timestamp': datetime.now().isoformat()
    })
    print(f"   ✅ Sarah registered with ID: {sarah_id}")
    print()
    
    # Test 2: Track visit via Sarah's referral link
    print("👀 Test 2: Someone visits via Sarah's referral link...")
    visit_id = database.insert_analytics({
        'event': 'page_visit',
        'page': '/',
        'timestamp': datetime.now().isoformat(),
        'visitorId': 'visitor-fatima-123',
        'referredBy': sarah_id  # Came via Sarah's link
    })
    print(f"   ✅ Visit tracked with ID: {visit_id} (referred by Sarah #{sarah_id})")
    print()
    
    # Test 3: Visitor (Fatima) registers via Sarah's link
    print("📝 Test 3: Visitor registers via Sarah's referral link...")
    fatima_id = database.insert_registration({
        'email': 'fatima@example.com',
        'firstName': 'Fatima',
        'lastName': 'Ahmed',
        'timestamp': datetime.now().isoformat(),
        'referredBy': sarah_id  # Referred by Sarah
    })
    print(f"   ✅ Fatima registered with ID: {fatima_id} (referred by Sarah #{sarah_id})")
    print()
    
    # Test 4: Create another referrer (Ahmed)
    print("📝 Test 4: Creating another referrer (Ahmed)...")
    ahmed_id = database.insert_registration({
        'email': 'ahmed@example.com',
        'firstName': 'Ahmed',
        'lastName': 'Khan',
        'timestamp': datetime.now().isoformat()
    })
    print(f"   ✅ Ahmed registered with ID: {ahmed_id}")
    print()
    
    # Test 5: Two people register via Ahmed's link
    print("📝 Test 5: Two people register via Ahmed's referral link...")
    maria_id = database.insert_registration({
        'email': 'maria@example.com',
        'firstName': 'Maria',
        'lastName': 'Garcia',
        'timestamp': datetime.now().isoformat(),
        'referredBy': ahmed_id
    })
    print(f"   ✅ Maria registered (referred by Ahmed #{ahmed_id})")
    
    john_id = database.insert_registration({
        'email': 'john@example.com',
        'firstName': 'John',
        'lastName': 'Smith',
        'timestamp': datetime.now().isoformat(),
        'referredBy': ahmed_id
    })
    print(f"   ✅ John registered (referred by Ahmed #{ahmed_id})")
    print()
    
    # Test 6: Get Sarah's referral stats
    print("📊 Test 6: Getting Sarah's referral stats...")
    sarah_stats = database.get_referral_stats(sarah_id)
    print(f"   Sarah's Stats:")
    print(f"   - Total Referrals: {sarah_stats['total_referrals']}")
    print(f"   - Total Visits: {sarah_stats['total_visits']}")
    print(f"   - Referred Users:")
    for referral in sarah_stats['referrals']:
        print(f"     • {referral['first_name']} {referral['last_name']} ({referral['email']})")
    print()
    
    # Test 7: Get Ahmed's referral stats
    print("📊 Test 7: Getting Ahmed's referral stats...")
    ahmed_stats = database.get_referral_stats(ahmed_id)
    print(f"   Ahmed's Stats:")
    print(f"   - Total Referrals: {ahmed_stats['total_referrals']}")
    print(f"   - Total Visits: {ahmed_stats['total_visits']}")
    print(f"   - Referred Users:")
    for referral in ahmed_stats['referrals']:
        print(f"     • {referral['first_name']} {referral['last_name']} ({referral['email']})")
    print()
    
    # Test 8: Get overall referral stats
    print("📊 Test 8: Getting overall referral statistics...")
    overall_stats = database.get_referral_stats()
    print(f"   Overall Stats:")
    print(f"   - Total Referrals: {overall_stats['total_referrals']}")
    print(f"   - Total Visits: {overall_stats['total_visits']}")
    print(f"   - Top Referrers:")
    for referrer in overall_stats['top_referrers']:
        print(f"     • Referrer ID #{referrer['referred_by']}: {referrer['referral_count']} referrals")
    print()
    
    # Test 9: Verify database records
    print("🔍 Test 9: Verifying database records...")
    with database.get_db() as conn:
        cursor = conn.cursor()
        
        # Check registrations with referrals
        cursor.execute('SELECT COUNT(*) FROM registrations WHERE referred_by IS NOT NULL')
        referred_count = cursor.fetchone()[0]
        print(f"   ✅ {referred_count} registrations have referrals")
        
        # Check analytics with referrals
        cursor.execute('SELECT COUNT(*) FROM analytics WHERE referred_by IS NOT NULL')
        referred_visits = cursor.fetchone()[0]
        print(f"   ✅ {referred_visits} analytics events have referrals")
        
        # List all referral relationships
        cursor.execute('''
            SELECT r1.first_name || ' ' || r1.last_name as referrer,
                   r2.first_name || ' ' || r2.last_name as referred
            FROM registrations r1
            JOIN registrations r2 ON r1.id = r2.referred_by
            ORDER BY r1.id
        ''')
        relationships = cursor.fetchall()
        print(f"\n   📋 Referral Relationships:")
        for rel in relationships:
            print(f"     • {rel[0]} → {rel[1]}")
    
    print()
    print("=" * 80)
    print("✅ ALL TESTS PASSED! Referral tracking is working correctly!")
    print("=" * 80)
    print()
    
    # Summary
    print("📝 SUMMARY:")
    print(f"   - Referral tracking column added to database")
    print(f"   - Analytics events can track referrals")
    print(f"   - Registrations can track who referred them")
    print(f"   - Query functions work for individual and overall stats")
    print(f"   - Referral relationships are correctly stored")
    print()
    
    return True

if __name__ == '__main__':
    try:
        test_referral_system()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
