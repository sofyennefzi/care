"""
Test dashboard page to see if it loads correctly
"""
import requests
from datetime import datetime

# Base URL
BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("TESTING DASHBOARD PAGE")
print("=" * 60)

# Create session
session = requests.Session()

# Login first
print("\n1. Logging in...")
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

# Test dashboard page
print("\n2. Testing dashboard page...")
try:
    response = session.get(f"{BASE_URL}/dashboard")
    print(f"   Dashboard response: {response.status_code}")

    if response.status_code == 200:
        content = response.text
        print(f"   ✅ Dashboard loaded successfully")

        # Check if the charts are in the HTML
        if 'rdvParJourChart' in content:
            print("   ✅ Bar chart element found in HTML")
        else:
            print("   ❌ Bar chart element NOT found in HTML")

        if 'topServicesChart' in content:
            print("   ✅ Donut chart element found in HTML")
        else:
            print("   ❌ Donut chart element NOT found in HTML")

        # Check if Chart.js data is present
        if 'rdv_par_jour' in content:
            print("   ✅ RDV par jour data found in HTML")
        else:
            print("   ❌ RDV par jour data NOT found in HTML")

        if 'top_services' in content:
            print("   ✅ Top services data found in HTML")
        else:
            print("   ❌ Top services data NOT found in HTML")

        # Check for console.log statements
        if 'console.log' in content:
            print("   ✅ Debug logging found in HTML")
        else:
            print("   ❌ Debug logging NOT found in HTML")

    else:
        print(f"   ❌ Dashboard failed to load: {response.status_code}")
        print(f"   Response: {response.text[:500]}")

except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("INSTRUCTIONS:")
print("1. Start your app: python main.py")
print("2. Open: http://127.0.0.1:8000/dashboard")
print("3. Open browser console (F12) to see debug logs")
print("4. Look for the console.log messages to see chart data")
print("=" * 60)
