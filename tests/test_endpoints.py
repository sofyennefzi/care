import sys
import os
# Ensure project root is on sys.path so `import main` works when running from tests/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
import json
import traceback

import main

client = TestClient(main.app)
paths = ['/login','/dashboard','/clients','/rdv','/agenda','/paiements']
for p in paths:
    try:
        r = client.get(p, allow_redirects=True)
        print(f'PATH {p} STATUS {r.status_code} LEN {len(r.content)}')
        if r.status_code >= 400:
            print('BODY (truncated):')
            print(r.text[:2000])
    except Exception:
        print('EXCEPTION for', p)
        traceback.print_exc()

# Try login (admin credentials from quick_seed)
r = client.post('/login', data={'username':'admin','password':'admin123'}, allow_redirects=False)
print('\nPOST /login', r.status_code)
print('Location:', r.headers.get('location'))
print('Set-Cookie:', r.headers.get('set-cookie'))
print('Body snippet:', r.text[:500])

# Try agenda API feed with sample dates
r = client.get('/api/agenda', params={'start':'2025-10-01T00:00:00Z','end':'2025-11-30T00:00:00Z'})
print('\nGET /api/agenda', r.status_code)
try:
    events = r.json()
    print('Events count:', len(events))
    if events:
        print('Sample event:', json.dumps(events[0], indent=2)[:400])
except Exception:
    print('Could not parse JSON; body:', r.text[:500])
