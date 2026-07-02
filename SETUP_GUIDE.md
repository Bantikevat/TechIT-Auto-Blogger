# 🚀 TechIT Auto-Blogger — Setup Guide

> **Owner:** Banti Kevat (TechIT — Tech in Hindi)
> **Purpose:** Naya laptop / naya system pe complete setup karne ka step-by-step guide
> **Time:** Total ~20 minutes (backup ke saath)

---

## 📌 Pehle YE SAMJHO (Important!)

### Aapka blog kahaan chalta hai?

```
❌ Aapke laptop pe NAHI chalta
✅ GitHub Actions (Microsoft cloud) pe chalta hai
```

**Iska matlab:**
- Laptop band ho / khoya jaaye / chori ho jaye → **Blog chalta rahega!** 🎉
- Roz 9:47 AM aur 6:17 PM IST — 2 posts automatic aayenge
- Sunday roadmap refresh automatic
- Google indexing, Telegram share — sab automatic

### Toh laptop pe kya karna padta hai?
- 🖥️ **Local scripts run karna** — jaise:
  - `python gemini_tools.py rewrite reference.txt` (koi post rewrite karna)
  - `python generate_roadmap.py` (roadmap regen)
  - `python refresh_old_posts.py 1` (purana post refresh)
- 🔧 **Code changes karna** aur GitHub pe push karna
- 🎨 **Theme edit + upload** karna

**Bina laptop ke bhi 90% cheezein chalengi!** Sirf 10% manual kaam ke liye laptop chahiye.

---

## 🔒 PART 1: Purane Laptop Se — Backup (5 min)

Ye **5 sensitive files** GitHub pe NAHI hain (security ke liye). **Naye laptop pe manually chahiye.**

### 📁 Backup karne wali files:

```
C:\Claude\AI_\
    ├─ blogger_credentials.json      ← Blogger OAuth (post karne ka permission)
    ├─ client_secrets.json           ← Google Cloud OAuth app credentials
    ├─ gemini_api_key.txt            ← AI content generate karne ki key
    ├─ google_indexing_sa.json       ← Google auto-indexing service account
    └─ imgbb_api_key.txt             ← Free image hosting key
```

**Kul size:** ~3 KB (bahut chhota!)

### 💾 Backup karne ke 3 tareeke (koi bhi choose karo):

#### Method A: Email to Self (RECOMMENDED — sabse aasaan)
1. Windows Explorer → `C:\Claude\AI_\` folder kholo
2. Upar 5 files select karo (`Ctrl+click` se ek-ek):
   - `blogger_credentials.json`
   - `client_secrets.json`
   - `gemini_api_key.txt`
   - `google_indexing_sa.json`
   - `imgbb_api_key.txt`
3. Right-click → **Send to → Compressed (zipped) folder**
4. Naam do: `techit-secrets-backup.zip`
5. Gmail kholo → khud ko email karo → zip file attach → **Send**
6. Subject: "TechIT secrets backup — [today's date]"

#### Method B: Google Drive
1. Upar wale steps 1-4 karo (zip banao)
2. Google Drive kholo → **Private folder** banao "TechIT Backup"
3. Upload karo `techit-secrets-backup.zip`
4. Folder ko **private** rakhna (share kabhi mat karna!)

#### Method C: USB Drive
1. Upar wale steps 1-4 karo
2. USB drive lagao
3. Zip file copy karo USB pe
4. USB safe jagah rakho

---

## 💻 PART 2: Naye Laptop Pe Setup (15 min)

### Step 1: Software Install Karo (5 min)

**1a. Python 3.10 ya higher install karo:**
- Kholo: https://python.org/downloads
- **Latest Python 3.x** download
- Install karte time **"Add Python to PATH"** checkbox ZAROOR tick karo!
- Verify: Terminal (Command Prompt) mein type karo:
  ```
  python --version
  ```
  Aana chahiye: `Python 3.10.x` ya higher

**1b. Git install karo:**
- Kholo: https://git-scm.com/downloads
- Windows waala download → next-next se install
- Verify:
  ```
  git --version
  ```

**1c. (Optional) GitHub CLI install karo:** *aage bahut kaam aayega*
- Kholo: https://cli.github.com/
- Windows installer download → install
- Login karo:
  ```
  gh auth login
  ```
  Choose: GitHub.com → HTTPS → Yes → **Login with a web browser** → Copy code → paste in browser → done!

---

### Step 2: Repository Clone Karo (2 min)

Terminal (Command Prompt) kholo aur ye commands chalao:

```
cd C:\
mkdir Claude
cd Claude
git clone https://github.com/Bantikevat/TechIT-Auto-Blogger.git AI_
cd AI_
```

Verify: `dir` command chalao — aapko `.py`, `.md`, folders sab dikhne chahiye.

---

### Step 3: Backup Files Wapas Rakho (3 min)

1. Purane laptop se jo `techit-secrets-backup.zip` bhejа tha (Email/Drive/USB se) — download/nikaalo
2. Zip kholo (right-click → Extract All)
3. Andar wali 5 files:
   - `blogger_credentials.json`
   - `client_secrets.json`
   - `gemini_api_key.txt`
   - `google_indexing_sa.json`
   - `imgbb_api_key.txt`
4. Sabko **copy karke `C:\Claude\AI_\` folder mein paste karo**

**Verify:**
```
cd C:\Claude\AI_
dir blogger_credentials.json gemini_api_key.txt imgbb_api_key.txt
```
Teeno files dikhni chahiye.

---

### Step 4: Python Packages Install Karo (5 min)

Terminal mein `C:\Claude\AI_` folder mein rehte hue:

```
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Yeh 3-5 min lega — Google API libraries, Pillow, requests install honge.

**Verify:**
```
python -c "import auto_post_blogger; print('OK')"
```
Output: `OK` → sab kaam kar raha!

---

### Step 5: Test Run (2 min)

Ek test post generate karke dekho ki sab kaam kar raha:

```
.venv\Scripts\activate
python gemini_tools.py topics 3
```

Agar 3 naye topics generate hoke `topics_to_write.txt` mein add ho gaye → **SETUP COMPLETE!** 🎉

---

## 🎯 Common Commands (yaad rakhne wale)

### Roz ke kaam:
```bash
# Environment activate (har baar pehle)
cd C:\Claude\AI_
.venv\Scripts\activate

# Manual post trigger (agar auto miss ho jaye)
gh workflow run auto_poster.yml --repo Bantikevat/TechIT-Auto-Blogger

# Roadmap page regen + update
python generate_roadmap.py

# Purana post refresh (SEO freshness)
python refresh_old_posts.py 1

# Broken images fix (all posts scan)
python fix_broken_images.py --scan

# Gemini tools
python gemini_tools.py topics 10                          # naye topic ideas
python gemini_tools.py captions "Post Title" "url"        # social captions
python gemini_tools.py faq "Post Title"                   # FAQ HTML
python gemini_tools.py rewrite "reference.txt"            # original post from reference
```

### Git commands:
```bash
# Latest code laao (agar aur commit hue hain)
git pull

# Code change kiya to push karo
git add .
git commit -m "your message here"
git push
```

### GitHub workflows manually chalane ke liye:
```bash
gh workflow run auto_poster.yml --repo Bantikevat/TechIT-Auto-Blogger
gh workflow run fix_images.yml --repo Bantikevat/TechIT-Auto-Blogger
gh workflow run refresh_posts.yml --repo Bantikevat/TechIT-Auto-Blogger
gh workflow run refresh_roadmap.yml --repo Bantikevat/TechIT-Auto-Blogger
```

---

## 🆘 Troubleshooting — Common Problems

### ❌ Problem 1: `python` command not found
**Solution:** Python install ke time PATH tick nahi ki thi.
- Python uninstall → wapas install → **"Add to PATH" TICK** zaroor karo.

### ❌ Problem 2: `git` command not found
**Solution:** Git install nahi hua ya PATH mein nahi hai.
- Git wapas install karo (default settings se).

### ❌ Problem 3: `pip install` fails
**Solution:** Venv activate nahi hua ya Python version bahut purana.
```
python -m venv .venv --clear
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### ❌ Problem 4: `invalid_grant: Token has been expired or revoked`
**Solution:** Blogger token expire ho gaya. Re-authorize karo:
```
python setup_blogger_api.py
```
Browser khulega → Google login → Allow → done.

Uske baad GitHub Secret bhi update karo:
```
gh secret set BLOGGER_CREDENTIALS_JSON --repo Bantikevat/TechIT-Auto-Blogger < blogger_credentials.json
```

### ❌ Problem 5: `gh: command not found`
**Solution:** GitHub CLI install karo: https://cli.github.com/
Ya browser se karo (github.com/Bantikevat/TechIT-Auto-Blogger/actions).

### ❌ Problem 6: Import errors when running scripts
**Solution:** Venv activate karna bhoole:
```
cd C:\Claude\AI_
.venv\Scripts\activate
```
Left side pe `(.venv)` dikhna chahiye.

---

## 🔐 Security Notes (Zaroori!)

### ✅ KYA SAFE HAI:
- ✅ GitHub repo PRIVATE hai — koi bhi random person code nahi dekh sakta
- ✅ 5 secret files `.gitignore` mein hain — kabhi GitHub pe nahi jaayengi
- ✅ GitHub Secrets encrypted hain — sirf workflows use kar sakte hain

### ❌ KYA NAHI KARNA:
- ❌ `blogger_credentials.json` public share MAT karna
- ❌ `gemini_api_key.txt` kisi ko forward MAT karna
- ❌ Chat/Slack/WhatsApp groups mein API keys paste MAT karna
- ❌ Backup zip password-protect karo agar public Cloud pe rakh rahe ho

### 🔄 Agar key leak ho jaye:
1. **Gemini key** — https://aistudio.google.com/ → key delete + new banao
2. **ImgBB key** — https://api.imgbb.com/ → delete + new banao
3. **Blogger creds** — `python setup_blogger_api.py` chalao (naya token milega)
4. **GitHub Secrets** wapas update karo:
   ```
   gh secret set GEMINI_API_KEY --repo Bantikevat/TechIT-Auto-Blogger --body "new-key"
   gh secret set IMGBB_API_KEY --repo Bantikevat/TechIT-Auto-Blogger --body "new-key"
   gh secret set BLOGGER_CREDENTIALS_JSON --repo Bantikevat/TechIT-Auto-Blogger < blogger_credentials.json
   ```

---

## 📁 Folder Structure (Reference)

Setup ke baad `C:\Claude\AI_\` mein ye hona chahiye:

```
C:\Claude\AI_\
├── .git\                            (Git tracking)
├── .github\workflows\               (5 auto-workflows)
│   ├── auto_poster.yml              (2x/day content gen)
│   ├── fix_images.yml               (monthly image check)
│   ├── refresh_posts.yml            (weekly SEO freshness)
│   ├── refresh_roadmap.yml          (Sunday roadmap regen)
│   └── weekly_report.yml            (SEO weekly report)
├── .venv\                           (Python virtual env — local only)
├── images\                          (banner images archive)
├── reports\                         (weekly SEO reports)
│
├── auto_post_blogger.py             (Main auto-poster)
├── refresh_old_posts.py             (Old post SEO refresh)
├── fix_broken_images.py             (Broken image detector)
├── generate_roadmap.py              (Learning path page gen)
├── gemini_tools.py                  (Topics/captions/faq/rewrite)
├── social_share.py                  (Multi-platform share)
├── cross_post.py                    (Dev.to/Hashnode cross-post)
├── bulk_index.py                    (Google index submit)
├── weekly_report.py                 (SEO analytics report)
├── cleanup_garbage_post.py          (Old junk post cleanup)
├── setup_blogger_api.py             (OAuth setup script)
│
├── posted_topics.json               (Posted topics tracker)
├── refreshed_posts.json             (Refresh cycle tracker)
├── topics_to_write.txt              (Content queue)
│
├── TechIT_Live_Theme.xml            (Blogger theme backup)
├── homepage_luxury_block.html       (Creator spotlight gadget)
├── roadmap.html                     (Learning path page HTML)
├── requirements.txt                 (Python dependencies)
├── run_auto_post.bat                (Local one-click runner)
├── SETUP_GUIDE.md                   (This file!)
│
├── blogger_credentials.json         (🔒 SECRET — backup!)
├── client_secrets.json              (🔒 SECRET — backup!)
├── gemini_api_key.txt               (🔒 SECRET — backup!)
├── google_indexing_sa.json          (🔒 SECRET — backup!)
└── imgbb_api_key.txt                (🔒 SECRET — backup!)
```

---

## 🎁 Quick Reference — Kaunsa Kaam Kaunse Command Se

| Kaam | Command |
|------|---------|
| Environment on karo | `.venv\Scripts\activate` |
| Naye topics banao | `python gemini_tools.py topics 10` |
| Ek post ka FAQ HTML banao | `python gemini_tools.py faq "Title"` |
| Social captions banao | `python gemini_tools.py captions "Title" "url"` |
| Reference se original post | `python gemini_tools.py rewrite reference.txt` |
| Roadmap page update | `python generate_roadmap.py` |
| Purana post refresh | `python refresh_old_posts.py 1` |
| Broken images fix | `python fix_broken_images.py` |
| Manual auto-post trigger | `gh workflow run auto_poster.yml --repo Bantikevat/TechIT-Auto-Blogger` |
| GitHub Secrets list dekho | `gh secret list --repo Bantikevat/TechIT-Auto-Blogger` |
| Blogger re-authorize | `python setup_blogger_api.py` |

---

## 🎉 SETUP COMPLETE — Ab kya?

### Roz check karo:
1. **Blog pe posts aa rahe hain kya?** — https://itinfohubs.blogspot.com/
2. **Search Console kya keh raha?** — https://search.google.com/search-console
3. **Auto-poster runs successful?** — https://github.com/Bantikevat/TechIT-Auto-Blogger/actions

### Weekly:
1. **SEO report padho** — `reports/` folder mein saved
2. **Roadmap page dekho** — https://itinfohubs.blogspot.com/p/learning-roadmap-techit-ka-complete.html
3. **Purane posts refresh hue check karo**

### Monthly:
1. **AdSense earnings dekho**
2. **Naye backlinks banao** (Quora, Reddit, communities)
3. **Ek real case-study post likho** (aapke real project pe)

---

## 🙏 Yaad Rakho:

> **Code sirf 10% hai. Content + Consistency = 90% hai.**
> 
> Aapka setup **top 1% bloggers se better** hai. Ab **6 mahine patience** rakho — TechIT India mein zaroor top karega! 🇮🇳👑

---

**Made with ❤️ for TechIT — Tech in Hindi**

**Last Updated:** 2026-07-02
