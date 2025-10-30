"""
Quick test to verify services API is working
Run this AFTER starting the server with: python main.py
"""
import requests
import time

def test_services():
    base = 'http://127.0.0.1:8000'

    print("🔍 Testing Services API...\n")

    # Step 1: Login
    print("1️⃣ Logging in...")
    s = requests.Session()
    try:
        r = s.post(base + '/login', data={'username':'admin','password':'admin123'}, timeout=5)
        if r.status_code == 302:
            print("   ✅ Login successful")
        else:
            print(f"   ❌ Login failed: {r.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server!")
        print("   👉 Make sure to run: python main.py")
        return False

    # Step 2: Test Services API
    print("\n2️⃣ Testing /api/services...")
    try:
        r = s.get(base + '/api/services', timeout=5)
        if r.status_code == 200:
            services = r.json()
            print(f"   ✅ SUCCESS! Loaded {len(services)} services")
            print("\n📋 Services available:")
            for svc in services:
                status_icon = "🟢" if svc.get('actif', False) else "🔴"
                print(f"   {status_icon} {svc['nom']}: {svc['prix_base']} TND")
            return True
        else:
            print(f"   ❌ ERROR: Status {r.status_code}")
            print(f"   Response: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🏥 CLINIC APP - Services API Test")
    print("="*60 + "\n")

    success = test_services()

    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("\n💡 Next step: Open browser and go to:")
        print("   http://localhost:8000/agenda")
        print("   Click 'Ajouter RDV' - services should appear!")
    else:
        print("❌ TEST FAILED!")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure server is running: python main.py")
        print("   2. Check for errors in server console")
        print("   3. Verify database has services: python quick_seed.py")
    print("="*60)

