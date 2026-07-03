import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
r = requests.get('https://www.google.com/search?q=satetapongsanguansuk&hl=en', headers=headers, timeout=5)
soup = BeautifulSoup(r.text, 'html.parser')

print('All links containing facebook:')
for a in soup.find_all('a'):
    href = a.get('href', '')
    if 'facebook' in href:
        print('-', href)

print('All absolute non-google links:')
for a in soup.find_all('a'):
    href = a.get('href', '')
    if href.startswith('http') and 'google.com' not in href:
        print('-', href)
