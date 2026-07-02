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

### Supported Platforms Overview

| Category | Platforms |
|----------|-----------|
| Social Media | Twitter, Instagram, Facebook, LinkedIn, TikTok, Reddit |
| Coding & Tech | GitHub, GitLab, Bitbucket, StackOverflow |
| Gaming | Steam, Twitch, Discord, Xbox Live |
| Audio/Video | YouTube, SoundCloud, Vimeo, Spotify |
| Writing & Docs | Medium, WordPress, Blogger |
| Others | ... (total 95 platforms) |

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

![Sample Console Output](tol.png)

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
