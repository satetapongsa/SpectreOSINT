import re

with open('spectre_osint.py', 'r', encoding='utf-8') as f:
    content = f.read()

target_start = '    # Run Deep scan if requested'
target_end = '    return {\n        "found_profiles": results,\n        "gravatar": gravatar_info,\n        "domains": domains_info,\n        "dorks": dorks_info,\n        "discovered_aliases": list(discovered_aliases)\n    }'

replacement = '''    # Extracted Contacts
    emails = set()
    phones = set()
    
    # Extract from found profiles
    for r in results:
        meta = r.get("metadata", {})
        bio = meta.get("bio") or ""
        fullname = meta.get("fullname") or ""
        for m in EMAIL_PATTERN.findall(bio):
            if is_email_related(m, username):
                emails.add(m)
        for m in EMAIL_PATTERN.findall(fullname):
            if is_email_related(m, username):
                emails.add(m)
        for m in meta.get("found_emails", []):
            if is_email_related(m, username):
                emails.add(m)
        for m in PHONE_PATTERN.findall(bio):
            phones.add(m)
            
    elapsed_time = time.time() - start_time
    
    # Print Detailed CLI Breakdown
    cat_counts = {}
    for r in results:
        cat = r.get("category", "Others")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        
    print("-" * 75)
    print(f"{Colors.BOLD}{Colors.CYAN}Scan Summary (Elapsed Time: {elapsed_time:.2f}s):{Colors.ENDC}")
    print(f"  {Colors.GREEN}- Profiles Found: {found_count} platforms{Colors.ENDC}")
    for cat, cnt in sorted(cat_counts.items()):
        print(f"    * {cat}: {Colors.GREEN}{cnt}{Colors.ENDC} profiles")
    if emails:
        print(f"  {Colors.GREEN}- Extracted Emails: {', '.join(emails)}{Colors.ENDC}")
    if phones:
        print(f"  {Colors.GREEN}- Extracted Phones: {', '.join(phones)}{Colors.ENDC}")
    print("-" * 75)
    
    # Generate HTML Report
    # HTML report generation disabled per user request

    discovered_aliases = set()
    for r in results:
        meta = r.get("metadata", {})
        fname = meta.get("fullname")
        if fname:
            cleaned_handle = fname.strip().lower()
            if cleaned_handle and " " not in cleaned_handle and cleaned_handle != username.lower():
                if re.match(r"^[a-zA-Z0-9_\\-\\.]+$", cleaned_handle):
                    discovered_aliases.add(cleaned_handle)

    return {
        "found_profiles": results,
        "discovered_aliases": list(discovered_aliases)
    }'''

if target_start in content and target_end in content:
    start_idx = content.find(target_start)
    end_idx = content.find(target_end) + len(target_end)
    new_content = content[:start_idx] + replacement + content[end_idx:]
    with open('spectre_osint.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Success!')
else:
    print('Not found!')
