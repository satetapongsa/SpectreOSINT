import re

with open('scratch/google_exist.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Clean input tag values or queries so we only find actual search result hits
cleaned = re.sub(r'<input[^>]*>', '', text)
cleaned = re.sub(r'value="[^"]*"', '', cleaned)

print('satetapongsanguansuk in cleaned text:', 'satetapongsanguansuk' in cleaned.lower())
# Find all occurrences with surrounding characters
for match in re.finditer(re.escape('satetapongsanguansuk'), cleaned, re.IGNORECASE):
    print('Match:', cleaned[max(0, match.start()-50):min(len(cleaned), match.end()+50)])
