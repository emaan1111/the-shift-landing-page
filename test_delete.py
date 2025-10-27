"""
Test script to demonstrate delete functionality
"""

import requests
import json

BASE_URL = "http://127.0.0.1:3000"

print("🧪 Testing Delete Functionality\n")
print("=" * 80)

# Test 1: Get a registration
print("\n1️⃣  Getting registration #5...")
response = requests.get(f"{BASE_URL}/api/registration/5")
if response.status_code == 200:
    reg = response.json()
    print(f"   ✅ Found: {reg['email']} - {reg['first_name']} {reg['last_name']}")
elif response.status_code == 404:
    print(f"   ⚠️  Registration #5 not found (might have been deleted)")
else:
    print(f"   ❌ Error: {response.status_code}")

# Test 2: Get all registrations count
print("\n2️⃣  Counting all registrations...")
response = requests.get(f"{BASE_URL}/api/registrations")
if response.status_code == 200:
    registrations = response.json()
    print(f"   ✅ Total registrations: {len(registrations)}")
else:
    print(f"   ❌ Error: {response.status_code}")

# Test 3: Delete a registration (example - not actually deleting)
print("\n3️⃣  Example: How to delete registration #1")
print(f"   Command: DELETE {BASE_URL}/api/registration/1")
print(f"   Or in Python:")
print(f"   requests.delete('{BASE_URL}/api/registration/1')")

# Test 4: Get an analytics event
print("\n4️⃣  Getting analytics event #100...")
response = requests.get(f"{BASE_URL}/api/analytics/event/100")
if response.status_code == 200:
    event = response.json()
    print(f"   ✅ Found: {event['event']} on {event['page']}")
elif response.status_code == 404:
    print(f"   ⚠️  Event #100 not found")
else:
    print(f"   ❌ Error: {response.status_code}")

# Test 5: Get recent analytics events
print("\n5️⃣  Getting recent page visits...")
response = requests.get(f"{BASE_URL}/api/analytics/events?event=page_visit&limit=3")
if response.status_code == 200:
    events = response.json()
    print(f"   ✅ Found {len(events)} recent visits:")
    for event in events:
        print(f"      - ID {event['id']}: {event['page']} from {event.get('country', 'Unknown')}")
else:
    print(f"   ❌ Error: {response.status_code}")

print("\n" + "=" * 80)
print("\n✅ API Endpoints Available:")
print("\n📋 Registrations:")
print("   GET    /api/registrations           - Get all registrations")
print("   GET    /api/registration/<id>       - Get specific registration")
print("   DELETE /api/registration/<id>       - Delete specific registration")
print("\n📊 Analytics:")
print("   GET    /api/analytics/events        - Get all analytics events")
print("   GET    /api/analytics/event/<id>    - Get specific event")
print("   DELETE /api/analytics/event/<id>    - Delete specific event")
print("   GET    /api/analytics/stats         - Get statistics")
print("\n🔥 Example Delete Commands:")
print("   curl -X DELETE http://127.0.0.1:3000/api/registration/1")
print("   curl -X DELETE http://127.0.0.1:3000/api/analytics/event/100")
print("\n")
