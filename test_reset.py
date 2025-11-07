#!/usr/bin/env python3
"""Test the database reset API endpoint"""

import requests
import json

# Test the reset endpoint
print("Testing database reset endpoint...")
print("=" * 50)

try:
    response = requests.post('http://localhost:5001/api/database/reset')
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"\n✅ Reset successful!")
            print(f"   Deleted {result['deleted']['analytics']} analytics events")
            print(f"   Deleted {result['deleted']['registrations']} registrations")
        else:
            print(f"\n❌ Reset failed: {result.get('error')}")
    else:
        print(f"\n❌ HTTP Error: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to server. Is it running on port 5001?")
except Exception as e:
    print(f"❌ Error: {e}")
