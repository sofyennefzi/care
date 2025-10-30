import time
import requests

base = 'http://127.0.0.1:8000'

s = requests.Session()
for _ in range(10):
    try:
        r = s.get(base + '/login', timeout=3)
        print('GET /login', r.status_code)
        break
    except Exception:
        time.sleep(1)

r = s.post(base + '/login', data={'username':'admin','password':'admin123'}, allow_redirects=False)
print('POST /login', r.status_code, r.headers.get('Location'))

r = s.get(base + '/clients', allow_redirects=False)
print('GET /clients', r.status_code)
print(r.text[:500])

