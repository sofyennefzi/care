import requests
import sys

base = 'http://127.0.0.1:8000'

try:
    # Login first
    s = requests.Session()
    r = s.post(base + '/login', data={'username':'admin','password':'admin123'}, timeout=5)
    print(f'Login: {r.status_code}')

    # Test services API
    r = s.get(base + '/api/services', timeout=5)
    print(f'\n/api/services: {r.status_code}')

    if r.status_code == 200:
        services = r.json()
        print(f'✓ SUCCESS! Found {len(services)} services')
        for svc in services[:3]:
            print(f'  - {svc["nom"]}: {svc["prix_base"]} TND')
    else:
        print(f'✗ ERROR: {r.text[:200]}')

except requests.exceptions.ConnectionError:
    print('✗ ERROR: Cannot connect to server. Make sure it\'s running with: python main.py')
    sys.exit(1)
except Exception as e:
    print(f'✗ ERROR: {e}')
    sys.exit(1)

