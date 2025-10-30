import time
import requests

base = 'http://127.0.0.1:8000'

s = requests.Session()
# Login
r = s.post(base + '/login', data={'username':'admin','password':'admin123'}, allow_redirects=False)
print('POST /login', r.status_code, r.headers.get('Location'))

# Test services page
r = s.get(base + '/services')
print('GET /services', r.status_code, 'OK' if r.status_code == 200 else 'ERROR')

# Test services API
r = s.get(base + '/api/services')
print('GET /api/services', r.status_code)
if r.status_code == 200:
    services = r.json()
    print(f'  Found {len(services)} services')
    if services:
        print(f'  Sample: {services[0]["nom"]} - {services[0]["prix_base"]} TND')

# Test create service
new_service = {
    "nom": "Radiographie",
    "description": "Examen radiologique",
    "prix_base": 60.00,
    "actif": True
}
r = s.post(base + '/api/services', json=new_service)
print(f'\nPOST /api/services', r.status_code)
if r.status_code == 200:
    created = r.json()
    print(f'  Created service ID: {created["id"]} - {created["nom"]}')

    # Test update
    r = s.patch(base + f'/api/services/{created["id"]}', json={"prix_base": 65.00})
    print(f'PATCH /api/services/{created["id"]}', r.status_code)

    # Test get one
    r = s.get(base + f'/api/services/{created["id"]}')
    print(f'GET /api/services/{created["id"]}', r.status_code)
    if r.status_code == 200:
        updated = r.json()
        print(f'  Updated prix_base: {updated["prix_base"]} TND')

