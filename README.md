# SpectreOSINT

![SpectreOSINT Banner](spectre_osint_banner.png)

**SpectreOSINT** is a high-fidelity, advanced command-line OSINT tool designed for exact username scanning across 95+ popular digital platforms. In addition to check-in mapping, it implements automated DNS domain registration tracking and an **Advanced Mention & Comment Harvester** to trace public posts, tags, and comments referencing the target across the web with direct, clickable links.

---

## Key Features

- **95+ Platforms Scanned:** Checks a comprehensive database of tech, social, gaming, audio/video, and writing websites.
- **100% Exact Matching:** Incorporates advanced validation rules (redirect checks, soft-404 text parsing, and page title comparisons) to eliminate false positives.
- **WAF & Block Detection:** Automatically detects Cloudflare security challenges and labels them as `Access Blocked` instead of reporting them as found or missing.
- **Advanced Mention & Comment Harvester:** Scans search engine indexes in parallel using ThreadPools to locate public comments, tags, check-ins, and references on social media (Facebook, Twitter/X, Instagram, LinkedIn, Reddit, etc.) with domain origin tags.
- **Zero Web Server Bloat:** 100% native terminal application, extremely lightweight, fast, and easy to run.

---

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SpectreOSINT.git
   cd SpectreOSINT
   ```

2. Install the dependencies:
   ```bash
   pip install requests beautifulsoup4
   ```

---

## How to Use

Run the script by passing the target username as an argument, or run it interactively:

### 1. Direct Search (Fastest)
```bash
python spectre_osint.py <target_username>
```
*Example:*
```bash
python spectre_osint.py satet
```

### 2. Interactive Search
```bash
python spectre_osint.py
```
This will prompt you to enter the username directly in the console.

---

## Sample Console Output

```text
               [ SpectreOSINT v3.0 ]
   Ultimate Username Hunter & Deep OSINT Search Tool

[*] Starting search for Username: satet ...
[*] Searching 95 platforms (Threads: 15, Timeout: 5.0s)
---------------------------------------------------------------------------
[+] [Social Media  ] Twitter/X       -> https://twitter.com/satet
[+] [Coding & Tech ] GitHub          -> https://github.com/satet
[+] [Others        ] Duolingo        -> https://www.duolingo.com/profile/satet
...

>>> Starting Deep Search (Mentions, Comments & Tags) <<<
[*] Checking Gravatar ID profile... [Found!]
[*] Searching matching domain registrations... [Found 4 registered domains]
    - Registered: satet.com, satet.net, satet.org, satet.xyz
[*] Harvesting public comments, tags, and posts...
 [+] Social Mentions & Tags (4 items found):
    1. [twitter.com] Satet (s_atet) / Twitter
       Link: https://twitter.com/s_atet
       Snippet: The latest Tweets from Satet...
    2. [pinterest.com] SATET (satet88) on Pinterest
       Link: https://www.pinterest.com/satet88/

---------------------------------------------------------------------------
Scan Summary (Elapsed Time: 13.91s):
  - Profiles Found: 25 platforms
  - Registered Domains: 4 domains
  - Profiles Not Found: 56 platforms
  - Errors/Blocked: 14 platforms
---------------------------------------------------------------------------
```

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
