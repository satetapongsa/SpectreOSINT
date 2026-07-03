with open('scratch/exist.html', 'r', encoding='utf-8') as f:
    exist_text = f.read()

with open('scratch/non.html', 'r', encoding='utf-8') as f:
    non_text = f.read()

print('exist_text size:', len(exist_text))
print('non_text size:', len(non_text))

# Let's check common keys in exist_text
keys_to_test = [
    'profile_id', 'profileid', 'userID', 'ownerID', 'fb://profile', 'fb://page',
    'entity_id', 'delegate_page', 'content_owner_id', 'profile_owner', 'typename',
    'User', 'Page', 'Group', 'Event', 'Message', 'Subscribe', 'Follow',
    'this page isn\'t available', 'broken link', 'link you followed', 'login', 'sign up'
]

for k in keys_to_test:
    print(f"Keyword '{k}': exist={k.lower() in exist_text.lower()}, non={k.lower() in non_text.lower()}")
