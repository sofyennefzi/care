import requests

print("Testing HTTP API endpoint...")
print("="*60)

base = 'http://127.0.0.1:8000'
s = requests.Session()

try:
    # Step 1: Login
    print("1. Logging in as admin...")
    r = s.post(base + '/login', data={'username':'admin','password':'admin123'}, timeout=5, allow_redirects=True)
    if r.status_code == 200 and 'Dashboard' in r.text:
        print(f"   ✅ Login successful (dashboard loaded)")
    elif r.status_code == 302:
        print(f"   ✅ Login successful (redirected to {r.headers.get('Location')})")
    else:
        print(f"   ❌ Login failed: {r.status_code}")
        print(f"   Response: {r.text[:200]}")
        exit(1)

    # Step 2: Test API
    print("\n2. Calling /api/services...")
    r = s.get(base + '/api/services', timeout=5)
    print(f"   Status code: {r.status_code}")

    if r.status_code == 200:
        services = r.json()
        print(f"   ✅ SUCCESS! Received {len(services)} services")
        for i, svc in enumerate(services[:3], 1):
            print(f"      {i}. {svc['nom']}: {svc['prix_base']} TND")
    else:
        print(f"   ❌ ERROR Response:")
        print(f"   {r.text}")

except requests.exceptions.ConnectionError as e:
    print(f"❌ Cannot connect to server at {base}")
    print("   Make sure server is running: python main.py")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("="*60)

