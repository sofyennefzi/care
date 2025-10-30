import time
import requests

base = 'http://127.0.0.1:8000'

s = requests.Session()
# Login
r = s.post(base + '/login', data={'username':'admin','password':'admin123'}, allow_redirects=False)
print('POST /login', r.status_code, r.headers.get('Location'))

# Test agenda page
r = s.get(base + '/agenda')
print('GET /agenda', r.status_code, 'OK' if r.status_code == 200 else 'ERROR')

# Test agenda API
r = s.get(base + '/api/agenda?start=2025-10-01&end=2025-11-30')
print('GET /api/agenda', r.status_code)
if r.status_code == 200:
    events = r.json()
    print(f'  Found {len(events)} events')
    if events:
        print(f'  Sample: {events[0]["title"]}')

