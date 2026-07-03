import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
r_exist = requests.get('https://www.facebook.com/satetapongsanguansuk/', headers=headers, timeout=5)
r_non = requests.get('https://www.facebook.com/cristiano_non_existent_random_1234567890/', headers=headers, timeout=5)

# Write both to files to inspect later
with open('scratch/exist.html', 'w', encoding='utf-8') as f:
    f.write(r_exist.text)

with open('scratch/non.html', 'w', encoding='utf-8') as f:
    f.write(r_non.text)

print('Done writing!')
