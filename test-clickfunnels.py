#!/usr/bin/env python3
"""
Test ClickFunnels Integration
"""

import requests
import json

# ClickFunnels Configuration (same as in server.py)
CLICKFUNNELS_CONFIG = {
    'apiKey': '7A8agApD4eXUESHF-ikrWlCF-k7IEjtTd7auzmiRbZ0',
    'workspaceId': 'jxRdRe',
    'teamId': 'JNqzOe',
    'tagIds': [367566],  # List-ShiftRegistered-Nov25
    'visitorTagIds': [367576]  # List-ShiftVisitiedNov24
}

def test_clickfunnels_api():
    """Test direct connection to ClickFunnels API"""
    print("🔍 Testing ClickFunnels API Connection...")
    print("=" * 80)
    
    # Test data
    test_contact = {
        'contact': {
            'email_address': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'tag_ids': CLICKFUNNELS_CONFIG['tagIds'],
            'fields': {
                'source': 'Test Script',
                'country': 'United States',
                'city': 'Test City'
            }
        }
    }
    
    url = f"https://api.myclickfunnels.com/api/v2/workspaces/{CLICKFUNNELS_CONFIG['workspaceId']}/contacts/upsert"
    
    headers = {
        'Authorization': f"Bearer {CLICKFUNNELS_CONFIG['apiKey']}",
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Test Script)'
    }
    
    print(f"📡 Sending request to: {url}")
    print(f"📧 Test email: {test_contact['contact']['email_address']}")
    print(f"🏷️  Tag IDs: {test_contact['contact']['tag_ids']}")
    print()
    
    try:
        response = requests.post(url, json=test_contact, headers=headers, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code in [200, 201]:
            print("✅ SUCCESS! ClickFunnels API is working!")
            print()
            print("Response Data:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print()
            print("Error Response:")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("❌ REQUEST TIMEOUT - ClickFunnels API is not responding")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR - Cannot reach ClickFunnels API: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("CLICKFUNNELS INTEGRATION TEST")
    print("=" * 80 + "\n")
    
    success = test_clickfunnels_api()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ ClickFunnels integration is configured correctly!")
        print("   You can safely use the registration form.")
    else:
        print("❌ ClickFunnels integration has issues.")
        print("   Please check your API key and configuration.")
    print("=" * 80 + "\n")
