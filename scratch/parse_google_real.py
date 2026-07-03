from bs4 import BeautifulSoup
import urllib.parse

def extract_links(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    for a in soup.find_all('a'):
        href = a.get('href', '')
        if href.startswith('/url?q='):
            # Parse Google redirect URL
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
            real_url = parsed.get('q', [None])[0]
            if real_url:
                results.append(real_url)
        elif href.startswith('http') and 'google.com' not in href:
            results.append(href)
    return results

print('Exist external links:', extract_links('scratch/google_exist.html'))
print('Non external links:', extract_links('scratch/google_non.html'))
