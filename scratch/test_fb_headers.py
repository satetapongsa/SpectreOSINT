import requests

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

exist_users = ['cristiano', 'taylorswift', 'satetapongsanguansuk']
non_exist_users = ['non_existent_rand_123', 'another_random_non_existent_456']

print('--- Existing Users ---')
for u in exist_users:
    r = requests.get(f'https://www.facebook.com/{u}/', headers=headers, timeout=5)
    has_coep = 'cross-origin-embedder-policy' in r.headers or 'cross-origin-embedder-policy-report-only' in r.headers
    print(u, 'COEP in headers:', has_coep, 'Status:', r.status_code)

print('--- Non-Existing Users ---')
for u in non_exist_users:
    r = requests.get(f'https://www.facebook.com/{u}/', headers=headers, timeout=5)
    has_coep = 'cross-origin-embedder-policy' in r.headers or 'cross-origin-embedder-policy-report-only' in r.headers
    print(u, 'COEP in headers:', has_coep, 'Status:', r.status_code)
