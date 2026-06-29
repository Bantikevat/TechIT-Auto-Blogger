# 🤖 TechIT MERN Stack Auto-Blogger

TechIT Auto-Blogger ek fully automated content generation aur publishing pipeline hai jo **Gemini AI** ka use karke high-quality programming tutorials (Hybrid Hindi-English language me) likhta hai aur use **Blogger API v3** ke zariye aapke blog par publish ya draft save karta hai.

Is project me ek dynamic **Google-grade Responsive Blogger Theme** (`TechIT_Theme.xml`) bhi shamil hai.

---

## ✨ Features

*   **Hybrid Hindi-English Writing:** AI articles ko clean Devanagari script aur English programming terms ke blend me likhta hai (100% natural human tone).
*   **Interactive Topic Selection:** Script chalaate hi aapse topic poochhegi. Aap apna topic de sakte hain ya sirf `Enter` daba kar system ko auto-select karne de sakte hain.
*   **Low-Competition SEO Targeter:** Script fallback list aur dynamic generator dono me sirf high-intent coding errors, debugging guides, aur modern frameworks comparisons (React 19 / Next.js) choose karegi.
*   **Google Indexing Autopilot:** Har post successfully publish hone ke baad script automatically Google search engines ko sitemap recrawl request send (ping) kar degi taaki faster indexing ho sake.
*   **Local Web Preview:** Publish hone se pehle local directory me `preview.html` file ban jaati hai taaki aap content aur search description copy kar sakein.
*   **Duplicate Title Guard:** Script dynamic checks lagati hai taaki pehle se posted topics dobara publish na hon.
*   **Auto SEO & FAQ Schema:** Har post ke end me FAQ sections aur Google Schema Markup JSON-LD automatically generate ho jaate hain.
*   **Daily Scheduling:** GitHub Actions se har subah 9:30 AM IST par automatic blogging.

---

## 🛠️ Local Setup (Installation)

### 1. Requirements Install Karein
Pehle virtual environment banayein aur dependecies install karein:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows par
pip install -r requirements.txt
```

### 2. API Credentials Configure Karein

#### A. Gemini API Key Setup:
*   [Google AI Studio](https://aistudio.google.com/) se free API Key generate karein.
*   Is directory me `gemini_api_key.txt` naam ki file banakar usme key paste kar dein (ya environment variable `GEMINI_API_KEY` set karein).

#### B. Blogger API Setup:
1.  [Google Cloud Console](https://console.cloud.google.com/) par ek project banayein.
2.  **Blogger API v3** search karke **Enable** karein.
3.  **Credentials** tab me jaakar **Create Credentials** -> **OAuth client ID** select karein.
4.  Application Type me **Desktop app** select karein aur name dekar credentials generate karein.
5.  JSON credentials download karke use `client_secrets.json` name se is folder me save karein.
6.  Setup helper script run karein:
    ```bash
    python setup_blogger_api.py
    ```
    *Ye aapka browser open karega. Sign-in karke authorize karein. Isse auto-poster ke liye `blogger_credentials.json` file generate ho jayegi.*

---

## 🚀 How to Run Locally

Niche di gayi command run karein:
```bash
.venv\Scripts\python auto_post_blogger.py
```
*   **Topic Selection:** Apna topic enter karein ya auto ke liye `Enter` press karein.
*   **Publish Settings:** `1` press karein Draft me save karne ke liye, ya `2` press karein Direct Live karne ke liye.
*   **Preview Content:** Run hone ke baad `preview.html` file par double-click karke check karein.

---

## ☁️ GitHub Actions Se Auto-Scheduling Setup

Agar aap chahte hain ki ye script daily automatic bina computer on kiye chale, toh is repository ko GitHub par push karein aur niche diye **Secrets** add karein:

1.  Apne GitHub Repository me jaayein -> **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**.
2.  Niche diye do secrets add karein:
    *   `GEMINI_API_KEY`: Aapki Gemini API key value.
    *   `BLOGGER_CREDENTIALS_JSON`: Aapki local `blogger_credentials.json` file ka poora text copy karke paste karein.

*Note: By default, GitHub Actions draft mode me save karega. Agar aap directly live publish karna chahte hain, toh repository me ek variable or environment variable `PUBLISH_LIVE` ko `true` set kar sakte hain.*

---

## 📂 Project Structure

*   `TechIT_Theme.xml` - Aapke blog ka high-speed, dark-themed responsive Blogger template.
*   `auto_post_blogger.py` - AI generation aur auto-posting ka main controller script.
*   `setup_blogger_api.py` - OAuth authentication setup helper.
*   `topics_to_write.txt` - Agar aap topics line-by-line queue me rakhna chahte hain.
*   `posted_topics.json` - Pehle se posted topics ka track log.
*   `requirements.txt` - Pythons packages/dependencies list.
*   `preview.html` - Local review file (generates dynamically).
