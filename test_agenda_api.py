"""
Quick test script for agenda API
"""
import requests
from datetime import datetime, timedelta

# Base URL
BASE_URL = "http://127.0.0.1:8000"

# Login first
session = requests.Session()

print("=" * 60)
print("TEST AGENDA API")
print("=" * 60)

# Try to login
print("\n1. Attempting login...")
login_data = {
    "username": "admin",
    "password": "admin123"
}

try:
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"   Login response: {response.status_code}")
    if response.status_code in [200, 302, 303, 307]:
        print("   ✅ Login successful")
    else:
        print(f"   ❌ Login failed: {response.text[:200]}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error during login: {e}")
    exit(1)

# Test agenda API
print("\n2. Testing /api/agenda endpoint...")

# Calculate date range (current month)
today = datetime.now()
start_date = today.replace(day=1)
next_month = start_date.replace(day=28) + timedelta(days=4)
end_date = next_month.replace(day=1)

start_str = start_date.strftime('%Y-%m-%d')
end_str = end_date.strftime('%Y-%m-%d')

print(f"   Date range: {start_str} to {end_str}")

try:
    url = f"{BASE_URL}/api/agenda?start={start_str}&end={end_str}"
    print(f"   URL: {url}")

    response = session.get(url)
    print(f"   Response status: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! Found {len(data)} events")

        if len(data) > 0:
            print(f"\n   First 3 events:")
            for i, event in enumerate(data[:3]):
                print(f"   {i+1}. {event.get('title')} - {event.get('start')}")
        else:
            print("   ℹ️ No events found in this period")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response body: {response.text[:500]}")

except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

