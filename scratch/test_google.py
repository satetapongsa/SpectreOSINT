import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
r_exist = requests.get('https://www.google.com/search?q="facebook.com/satetapongsanguansuk"&hl=en', headers=headers, timeout=5)
r_non = requests.get('https://www.google.com/search?q="facebook.com/cristiano_non_existent_random_1234567890"&hl=en', headers=headers, timeout=5)

soup_e = BeautifulSoup(r_exist.text, 'html.parser')
soup_n = BeautifulSoup(r_non.text, 'html.parser')

print('Exist Title:', soup_e.title.string if soup_e.title else 'None')
print('Non Title:', soup_n.title.string if soup_n.title else 'None')

# Print body text snippets
print('Exist contains Google Search:', 'google search' in r_exist.text.lower())
print('Non contains Google Search:', 'google search' in r_non.text.lower())

# Save HTML files to inspect
with open('scratch/google_exist.html', 'w', encoding='utf-8') as f:
    f.write(r_exist.text)
with open('scratch/google_non.html', 'w', encoding='utf-8') as f:
    f.write(r_non.text)
