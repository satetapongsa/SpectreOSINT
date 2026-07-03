import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def check_bing_index(username):
    url = f'https://www.bing.com/search?q=site:facebook.com/{username}'
    r = requests.get(url, headers=headers, timeout=5)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Save the html to check
    with open(f'scratch/bing_{username}.html', 'w', encoding='utf-8') as f:
        f.write(r.text)
        
    for a in soup.find_all('a'):
        href = a.get('href', '')
        # Check if it links to the actual profile (excluding Bing search links themselves)
        if f'facebook.com/{username}' in href.lower() and 'bing.com' not in href.lower():
            return True
    return False

print('satetapongsanguansuk in Bing:', check_bing_index('satetapongsanguansuk'))
print('cristiano_non_existent in Bing:', check_bing_index('cristiano_non_existent_random_1234567890'))
