import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
r = requests.get('https://www.bing.com/search?q=satetapongsanguansuk', headers=headers, timeout=5)
soup = BeautifulSoup(r.text, 'html.parser')

print('Bing status:', r.status_code)
for idx, h2 in enumerate(soup.find_all('h2'), 1):
    a = h2.find('a')
    if a:
        title = a.text
        href = a.get('href', '')
        print(f"{idx}. {title.encode('utf-8')} -> {href}")
