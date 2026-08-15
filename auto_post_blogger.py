import os
import io
import json
import sys
import random

# Windows console pe Hindi/emoji clean print — cp1252 crash se bacha
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import base64
import subprocess
import urllib.parse
import requests
import time
import re

import social_share  # multi-platform auto-share (Twitter/X, Facebook, Pinterest)
import cross_post     # Dev.to / Hashnode cross-post for backlinks

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
except ImportError:
    print("ERROR: Required packages are not installed.")
    print("Please run: .venv\\Scripts\\pip install google-auth-oauthlib google-api-python-client google-auth-httplib2 requests")
    sys.exit(1)

# Configuration
BLOG_ID = "7779383721769805036"
TRACKER_FILE = "posted_topics.json"
CREDENTIALS_FILE = "blogger_credentials.json"
GEMINI_KEY_FILE = "gemini_api_key.txt"
QUEUE_FILE = "topics_to_write.txt"

# IndexNow key — generated in Bing Webmaster Tools (site already verified there, so no
# key file hosting needed). Override anytime with the INDEXNOW_KEY env var / GitHub Secret.
INDEXNOW_KEY_DEFAULT = "0db540fa14b34f7181150950ea7bbef9"

# Banner image generation — GitHub repo (used for CDN-hosted banners when ImgBB is not configured)
GITHUB_REPO = "Bantikevat/TechIT-Auto-Blogger"
ASSETS_DIR = "assets"
IMAGES_DIR = "images"


# Default topics to fallback on (low competition coding errors and modern debugging)
DEFAULT_TOPICS = [
    {"topic": "How to Fix Hydration failed because the initial UI does not match in NextJS", "category": "NextJS"},
    {"topic": "How to Fix MongooseError: Operation users.findOne() buffering timed out in Nodejs", "category": "Error Solving"},
    {"topic": "How to Fix CORS policy: No Access-Control-Allow-Origin header is present in MERN Stack", "category": "Error Solving"},
    {"topic": "How to Solve JWT expired Error with Axios Interceptors and Refresh Tokens", "category": "MERN Stack"},
    {"topic": "How to Fix React Hook useEffect has a missing dependency Lint Warning", "category": "Error Solving"},
    {"topic": "How to Fix Error: Cannot find module in Node.js ESM vs CommonJS", "category": "Error Solving"},
    {"topic": "How to Fix MongoDB connection failed on Render and Vercel Deployment", "category": "Error Solving"},
    {"topic": "React 19 Server Actions vs traditional API requests: When to use what", "category": "ReactJS"},
    {"topic": "How to Fix Express payload too large error when uploading base64 images", "category": "ExpressJS"},
    {"topic": "How to Fix Next.js API route returns 404 in production Vercel error", "category": "NextJS"}
]

def load_gemini_api_key():
    # 1. Check environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key
        
    # 2. Check local file
    if os.path.exists(GEMINI_KEY_FILE):
        with open(GEMINI_KEY_FILE, "r", encoding="utf-8") as f:
            api_key = f.read().strip()
            if api_key:
                return api_key
                
    # 3. Prompt user and save it
    print("==================================================")
    print("  Gemini API Key Setup  ")
    print("==================================================")
    print("Google AI Studio (https://aistudio.google.com/) se free Gemini API Key create karein.")
    api_key = input("Enter your Gemini API Key: ").strip()
    if api_key:
        with open(GEMINI_KEY_FILE, "w", encoding="utf-8") as f:
            f.write(api_key)
        print(f"Key successfully saved to '{GEMINI_KEY_FILE}'!\n")
        return api_key
    else:
        print("[ERROR] Gemini API Key is required to generate articles.")
        sys.exit(1)

def get_posted_topics():
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_posted_topic(topic):
    posted = get_posted_topics()
    posted.append(topic)
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(posted, f, indent=4)

def call_gemini(gemini_key, prompt):
    models = ["gemini-2.5-flash-latest", "gemini-1.5-flash", "gemini-1.5-flash-8b"]
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
        # Try up to 3 times for each model in case of rate limits / timeouts
        for attempt in range(3):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=150)
                if response.status_code == 200:
                    res_json = response.json()
                    text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                    return text
                elif response.status_code in [503, 429]:
                    sleep_sec = 5 * (attempt + 1)
                    print(f"[WARNING] Gemini model {model} returned {response.status_code} (attempt {attempt+1}/3). Retrying in {sleep_sec}s...")
                    time.sleep(sleep_sec)
                else:
                    print(f"[WARNING] Gemini model {model} returned status code {response.status_code}: {response.text[:200]}. Trying next option.")
                    break # Break out of attempt loop to try the next model
            except Exception as e:
                print(f"[WARNING] Error calling Gemini model {model}: {e}")
                time.sleep(3)
                
    return None

def classify_topic_category(gemini_key, topic):
    # Quick call to Gemini to classify the topic's category
    prompt = f"""
    Classify this programming tutorial topic: "{topic}"
    Choose EXACTLY one category from this list: ReactJS, NextJS, NodeJS, ExpressJS, MongoDB, Error Solving, MERN Stack.
    Output ONLY the category name (just a single word/phrase from the list). Do not output any other text or explanation.
    """
    category = call_gemini(gemini_key, prompt)
    if category:
        category = category.strip()
        # Clean up response
        for valid in ["ReactJS", "NextJS", "NodeJS", "ExpressJS", "MongoDB", "Error Solving", "MERN Stack"]:
            if valid.lower() in category.lower():
                return valid
    return "MERN Stack" # Default fallback

def normalize_title(title):
    # Convert to lowercase
    t = title.lower()
    # Remove dynamic suffixes and labels
    t = re.sub(r'\(in hindi\)|in hindi|tutorial|explained|guide|masterclass|introduction|basics|deep dive|step-by-step', '', t)
    # Remove special chars and non-alphanumeric characters, consolidate whitespace
    t = re.sub(r'[^a-z0-9]', '', t)
    return t.strip()

def refill_topic_queue(gemini_key, posted_topics, count=10):
    """Queue low ho to Gemini se naye low-competition topics generate karke append karo — pipeline kabhi na ruke.

    NOTE: Jab tak topics_to_write.txt me React related items hain, focus REACT-only rakho
    (roadmap.sh React series complete karne tak).
    """
    existing = set()
    react_focus = False
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                t = line.strip()
                if t and not t.startswith("#"):
                    existing.add(t.lower())
                    if "react" in t.lower() or "jsx" in t.lower() or "use" in t.lower():
                        react_focus = True
    for t in posted_topics:
        existing.add(str(t).lower())

    if react_focus:
        prompt = f"""You are an SEO expert for a HINDI React tutorial blog (audience: Indian devs learning React in Hinglish).
Give {count + 6} fresh REACT-ONLY blog post TITLE ideas following the roadmap.sh React learning path (hooks, routing, state management, styling, forms, API, testing, TypeScript, animations, React Native).
STRICT RULES:
- ONLY React topics (React, JSX, hooks, Router, Redux, Zustand, Tailwind, Material UI, React Hook Form, Axios, React Query, Testing, TypeScript with React, Framer Motion, React Native). NO Node/Mongo/Next standalone topics.
- Hinglish question style: "kaise use karein", "kya hai", "complete guide", "beginner friendly".
- Technical terms English me (React, useEffect, TanStack Query), framing Hinglish me. Long-tail (6-10 words).
- In already-written React topics se BILKUL alag: {[t for t in posted_topics if 'react' in str(t).lower() or 'jsx' in str(t).lower()][:40]}
Output ONLY plain text — ek line me ek title, numbering/bullets/extra text ke bina."""
    else:
        prompt = f"""You are an SEO expert for a HINDI programming blog (audience: beginner Indian developers, Hinglish search).
Give {count + 6} fresh, LOW-COMPETITION, long-tail blog post TITLE ideas about MERN stack (MongoDB, Express, React, Node.js), Next.js, JavaScript, AI tools, ya common coding errors aur unke solutions.
RULES:
- Hinglish (Roman Hindi) question style: "kya hai", "kaise kare", "kaise banaye", "error solution", "difference".
- Technical terms English me (React, useState, MongoDB, async), framing Hinglish me. Specific aur long-tail (5-9 words).
- Broad high-competition titles avoid karo (jaise "React Hooks Explained").
- In already-written topics se BILKUL alag: {list(posted_topics)[:40]}
Output ONLY plain text — ek line me ek title, numbering/bullets/extra text ke bina."""
    out = call_gemini(gemini_key, prompt)
    if not out:
        print("[WARNING] Topic refill: Gemini se response nahi mila.")
        return 0
    new = []
    for line in out.splitlines():
        t = re.sub(r'^[\s\-\*\d\.\)]+', '', line).strip().strip('"').strip("`")
        if t and t.lower() not in existing and len(t) > 8:
            existing.add(t.lower())
            new.append(t)
        if len(new) >= count:
            break
    if new:
        with open(QUEUE_FILE, "a", encoding="utf-8") as f:
            for t in new:
                f.write(t + "\n")
        print(f"[OK] Topic queue AUTO-REFILL: {len(new)} naye topics add hue (pipeline safe).")
    return len(new)


def select_topic(gemini_key, posted_topics):
    # 0. AUTO-REFILL: queue low ho to pehle bhar do (pipeline kabhi na ruke)
    try:
        qcount = 0
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                qcount = len([l for l in f if l.strip() and not l.strip().startswith("#")])
        if qcount < 5:
            print(f"[INFO] Topic queue low hai ({qcount} bache). Gemini se auto-refill ho raha hai...")
            refill_topic_queue(gemini_key, posted_topics, count=10)
    except Exception as e:
        print(f"[WARNING] Auto-refill skip: {e}")

    # 1. Try reading from custom topic queue file
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith("#")]
            
            if lines:
                selected_topic = lines[0]
                remaining_topics = lines[1:]
                
                # Write remaining topics back to keep queue updated
                with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                    for t in remaining_topics:
                        f.write(t + "\n")
                
                print(f"[OK] Found custom topic in queue: '{selected_topic}'")
                
                # Determine category using Gemini
                category = classify_topic_category(gemini_key, selected_topic)
                print(f"[OK] Topic classified as category: {category}")
                return selected_topic, category
        except Exception as e:
            print(f"[WARNING] Error reading topic queue: {e}")

    # 2. Fall back to dynamic selection if queue is empty or missing
    print("[INFO] Queue file khali/missing hai. Topic dynamically select kiya ja raha hai...")
    
    # Normalize already posted topics to prevent duplicates
    normalized_posted = [normalize_title(t) for t in posted_topics]
    
    for attempt in range(3):
        prompt = f"""
        You are an SEO expert for a HINDI programming blog (audience: beginner Indian developers and students who search in Hindi/Hinglish).
        Choose ONE highly-searchable, LOW-COMPETITION blog topic about MERN stack (MongoDB, Express, React, Node.js), Next.js, JavaScript, or common coding errors.

        CRITICAL SEO RULES (yeh blog naya hai, isliye low-competition long-tail zaroori hai):
        - Phrase the topic the way a real Hindi-speaking beginner would SEARCH on Google — use Hinglish (Roman Hindi) question style.
        - Prefer "kya hai", "kaise kare", "kaise banaye", "ka matlab", "difference", "error solution" style queries.
        - Keep technical terms (React, useState, MongoDB, async) in English, but the question framing in Hinglish.
        - Be VERY specific and long-tail (5-9 words). Avoid broad, high-competition English titles that compete with Stack Overflow / Medium.
        - The topic must NOT be in this already-written list: {posted_topics}. Pick a clearly different concept for variety.

        GOOD examples (low competition, Hindi-search friendly):
        {{"topic": "Next.js me Hydration Error kaise solve kare", "category": "NextJS"}}
        {{"topic": "useEffect Hook kya hai aur kab use kare", "category": "ReactJS"}}
        {{"topic": "MongoDB connection timeout error ka solution Hindi me", "category": "Error Solving"}}
        BAD examples (too broad / high competition — avoid): "React Hooks Explained", "How to use Express.js".

        Output ONLY raw JSON (no markdown, no backticks): {{"topic": "...", "category": "..."}}
        category MUST be exactly one of: ReactJS, NextJS, NodeJS, ExpressJS, MongoDB, Error Solving, MERN Stack.
        """
        
        text = call_gemini(gemini_key, prompt)
        if text:
            try:
                # Clean up potential markdown formatting backticks
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                
                data = json.loads(text)
                selected_topic = data["topic"]
                category = data["category"]
                
                # Normalize and check for duplicate
                norm_selected = normalize_title(selected_topic)
                if norm_selected in normalized_posted:
                    print(f"[WARNING] Selected topic '{selected_topic}' normalized to '{norm_selected}' which matches an already written topic. Retrying...")
                    continue
                
                print(f"[OK] Gemini dynamically selected topic: '{selected_topic}' (Category: {category})")
                return selected_topic, category
            except Exception as e:
                print(f"[WARNING] Failed to parse Gemini response: {e}")
                
    # Fallback to defaults if dynamic selection fails or repeats
    available = [t for t in DEFAULT_TOPICS if normalize_title(t["topic"]) not in normalized_posted]
    if not available:
        available = DEFAULT_TOPICS
        
    choice = random.choice(available)
    print(f"[OK] Selected fallback topic: '{choice['topic']}' (Category: {choice['category']})")
    return choice["topic"], choice["category"]

def _slugify(text, maxlen=55):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')
    return (s[:maxlen].strip('-')) or "techit-post"


def _load_font(kind, size):
    # Poppins fonts assets/ folder me committed hain. Na milein to default font.
    from PIL import ImageFont
    path = os.path.join(ASSETS_DIR, f"Poppins-{kind}.ttf")
    if not os.path.exists(path):
        # Runtime download fallback (agar assets/ commit nahi hua)
        urls = {
            "Bold": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf",
            "SemiBold": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-SemiBold.ttf",
            "Regular": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
        }
        try:
            os.makedirs(ASSETS_DIR, exist_ok=True)
            r = requests.get(urls.get(kind, urls["Bold"]), timeout=30)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
        except Exception as e:
            print(f"[WARNING] Font '{kind}' download failed: {e}")
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _wrap_text(draw, text, font, max_width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def generate_bg_prompt(gemini_key, clean_title):
    # AI sirf BACKGROUND banaye (koi text nahi — kyunki AI text spell nahi kar pata, garble ho jata hai).
    prompt = f"""Create a short English image prompt for a BACKGROUND graphic for a tech blog about "{clean_title}".
    Describe a modern premium tech background: abstract code, circuit patterns, glowing UI elements, depth/bokeh, dark navy theme with cyan, blue and purple neon accents, 3D render or clean flat vector style.
    CRITICAL: The image must contain absolutely NO text, NO letters, NO words, NO typography — only visuals and graphics.
    Output ONLY the one-sentence prompt, nothing else."""
    p = call_gemini(gemini_key, prompt)
    if p:
        p = p.strip().replace('"', '').replace('\n', ' ')
        return f"{p}, absolutely no text, no words, no letters, clean abstract tech background, dark navy, cyan neon glow, ultra detailed, high quality, professional"
    return f"abstract modern tech background related to {clean_title}, circuit board, glowing cyan and blue neon lines, dark navy gradient, depth, no text, no words, 3d render, ultra detailed"


def fetch_ai_background(gemini_key, clean_title, seed):
    # Flux model + random seed = har baar UNIQUE high-quality background (same image problem fix).
    bg_prompt = generate_bg_prompt(gemini_key, clean_title)
    url = (f"https://image.pollinations.ai/prompt/{urllib.parse.quote(bg_prompt)}"
           f"?width=1200&height=630&nologo=true&model=flux&seed={seed}&enhance=true")
    try:
        r = requests.get(url, timeout=120)
        if r.status_code == 200 and r.content:
            return r.content, url
        print(f"[INFO] Background fetch status {r.status_code}, will use URL directly.")
    except Exception as e:
        print(f"[WARNING] Background image fetch failed: {e}")
    return None, url


def compose_banner(bg_bytes, clean_title, category):
    # AI background ke upar ASLI title text + category badge + brand overlay — perfectly readable.
    from PIL import Image, ImageDraw
    W, H = 1200, 630
    if bg_bytes:
        img = Image.open(io.BytesIO(bg_bytes)).convert("RGB").resize((W, H))
    else:
        img = Image.new("RGB", (W, H), (13, 27, 42))

    # Dark gradient overlay (neeche zyada dark) — text contrast ke liye
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(70 + 150 * (y / H)))
    alpha = grad.resize((W, H))
    img = Image.composite(Image.new("RGB", (W, H), (7, 12, 24)), img, alpha)

    draw = ImageDraw.Draw(img)

    # Category badge (top-left, cyan)
    badge_font = _load_font("SemiBold", 30)
    cat = category.upper()
    cw = draw.textlength(cat, font=badge_font)
    draw.rounded_rectangle([60, 56, 60 + cw + 52, 56 + 54], radius=27, fill=(6, 182, 212))
    draw.text((60 + 26, 56 + 11), cat, font=badge_font, fill=(4, 18, 28))

    # CTA — top-right (bigger yellow badge for click-through, OCR-friendly English)
    cta_font = _load_font("Bold", 34)
    cta_text = "READ NOW →"
    ctw = draw.textlength(cta_text, font=cta_font)
    cta_pad_x, cta_pad_y = 30, 15
    cta_h = 62
    cta_x = W - 60 - ctw - (cta_pad_x * 2)
    # Yellow gradient-like double-layer for depth
    draw.rounded_rectangle([cta_x + 4, 60 + 4, W - 60 + 4, 60 + cta_h + 4], radius=31, fill=(0, 0, 0, 100))  # shadow
    draw.rounded_rectangle([cta_x, 60, W - 60, 60 + cta_h], radius=31, fill=(255, 204, 0))
    draw.text((cta_x + cta_pad_x, 60 + cta_pad_y), cta_text, font=cta_font, fill=(20, 20, 20))

    # Title — auto-fit font size so it wraps in <= 4 lines
    title_font, lines = None, []
    for fs in (70, 62, 54, 48, 42):
        f = _load_font("Bold", fs)
        wrapped = _wrap_text(draw, clean_title, f, W - 120)
        if len(wrapped) <= 4:
            title_font, lines = f, wrapped
            break
    if title_font is None:
        title_font = _load_font("Bold", 42)
        lines = _wrap_text(draw, clean_title, title_font, W - 120)[:4]

    lh = int(title_font.size * 1.16)
    y = H - 150 - len(lines) * lh
    for ln in lines:
        draw.text((63, y + 3), ln, font=title_font, fill=(0, 0, 0))      # shadow
        draw.text((60, y), ln, font=title_font, fill=(255, 255, 255))    # text
        y += lh

    # Brand bottom-left
    brand_font = _load_font("Bold", 36)
    draw.text((60, H - 82), "</> TechIT", font=brand_font, fill=(6, 182, 212))
    sub_font = _load_font("Regular", 26)
    bw = draw.textlength("</> TechIT", font=brand_font)
    draw.text((60 + bw + 16, H - 76), "Tech in Hindi", font=sub_font, fill=(150, 170, 190))

    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


def upload_to_imgbb(png_bytes, api_key):
    # Free ImgBB host — instant CDN URL (best option, ordering issue nahi).
    try:
        b64 = base64.b64encode(png_bytes).decode()
        r = requests.post("https://api.imgbb.com/1/upload", timeout=60,
                          data={"key": api_key, "image": b64})
        if r.status_code == 200:
            return r.json()["data"]["url"]
        print(f"[WARNING] ImgBB returned {r.status_code}: {r.text[:150]}")
    except Exception as e:
        print(f"[WARNING] ImgBB upload failed: {e}")
    return None


def save_banner_to_repo(png_bytes, slug, seed):
    # ImgBB na ho to image repo me save + (Actions me) turant push -> raw.githubusercontent URL.
    os.makedirs(IMAGES_DIR, exist_ok=True)
    fname = f"{slug}-{seed}.png"
    path = os.path.join(IMAGES_DIR, fname)
    with open(path, "wb") as f:
        f.write(png_bytes)
    raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{IMAGES_DIR}/{fname}"
    if os.environ.get("GITHUB_ACTIONS"):
        # Image ko post-publish se pehle push karo taaki URL turant resolve ho
        try:
            subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=False)
            subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=False)
            subprocess.run(["git", "add", path], check=False)
            subprocess.run(["git", "commit", "-m", f"Add banner image {fname} [skip ci]"], check=False)
            subprocess.run(["git", "push"], check=False)
            print(f"[OK] Banner image repo me push hui: {raw_url}")
        except Exception as e:
            print(f"[WARNING] git push image failed: {e}")
    return raw_url


def generate_banner(gemini_key, topic, category):
    # Pura banner pipeline: AI background -> real title overlay -> host. Fail-safe with fallbacks.
    clean_title = topic.replace("(In Hindi)", "").replace("(in Hindi)", "").strip()
    seed = random.randint(1, 999999)
    print(f"[INFO] Banner generate ho raha hai (seed={seed}) for: '{clean_title}'")

    bg_bytes, bg_url = fetch_ai_background(gemini_key, clean_title, seed)

    try:
        png = compose_banner(bg_bytes, clean_title, category)
    except Exception as e:
        print(f"[WARNING] Banner compose fail ({e}). Plain AI image use ho rahi hai.")
        return bg_url  # fallback: direct pollinations background (varied, clean, no garbled text)

    # ImgBB key: pehle env var (GitHub Actions secret), warna local file (gitignored)
    imgbb_key = os.environ.get("IMGBB_API_KEY", "").strip()
    if not imgbb_key and os.path.exists("imgbb_api_key.txt"):
        with open("imgbb_api_key.txt", "r", encoding="utf-8") as f:
            imgbb_key = f.read().strip()
    if imgbb_key:
        url = upload_to_imgbb(png, imgbb_key)
        if url:
            print(f"[OK] Banner ImgBB par upload hui: {url}")
            return url

    return save_banner_to_repo(png, _slugify(clean_title), seed)

def fix_html_tags(html):
    # Balanced check for unclosed HTML tags to prevent XML syntax errors in Blogger theme
    tags = ['div', 'p', 'span', 'h2', 'h3', 'ul', 'li', 'pre', 'code', 'details', 'summary']
    for tag in tags:
        open_count = len(re.findall(rf'<{tag}\b', html))
        close_count = len(re.findall(rf'</{tag}>', html))
        if open_count > close_count:
            # Append missing closing tags to repair the HTML structure
            html += f"</{tag}>" * (open_count - close_count)
    return html

def generate_article_content(gemini_key, topic, category):
    print(f"[INFO] Article content generate kiya ja raha hai for: '{topic}'...")
    
    # 1. Generate a professional banner: AI background + REAL title text overlay (readable, unique)
    banner_url = generate_banner(gemini_key, topic, category)
    print(f"[OK] Banner URL: {banner_url}")
    
    prompt = f"""
    Write a highly detailed, professional, long-form (at least 1500 to 2500 words), and extremely easy-to-read programming blog tutorial about: "{topic}" (Category: {category}) in Hybrid Hindi-English.
    
    Language & Script Requirements:
    - Write the main sentences in clean Devanagari Hindi script (हिंदी लिपि).
    - Keep all technical terms, coding keywords, library names, and variables in raw English (Latin script). For example: write "React Context API", "Prop Drilling", "State Management", "useContext Hook", "Mongoose Schema" in English, while the surrounding explanation is in Devanagari Hindi.
    
    Tone Requirements:
    - Write as if you are a senior developer with 50 years of experience, pair-programming with a close friend. Use terms like "दोस्तों", "चलिए शुरू करते हैं", "कैसे काम करता है", "ध्यान देने वाली बात ये है कि".
    - 100% human tone. Avoid generic AI transitions or structures like "निष्कर्ष", "अंतिम विचार", "आशा है कि यह ब्लॉग आपको पसंद आया होगा". Write naturally.
    
    Depth & Content Length Requirements:
    - The article must be extremely long-form, detailed, and comprehensive (Master-class tutorial style).
    - Write deep, step-by-step explanations of the topic. Why do we use it? What problem does it solve?
    - Provide complete, production-ready, and fully-functional coding examples. Do NOT use comments like "// write code here" or truncate/summarize the code. Write every line of the code clearly.
    - Discuss edge cases, common errors developers face when using this, and how to debug/solve them.
    - Include best practices for performance and scalability.

    FIRST-PAGE GOOGLE RANKING (MOST IMPORTANT — yeh blog ko #1 rank karwata hai):
    - **META HOOK LINE (FIRST paragraph — CRITICAL):** Post ki bilkul PEHLI line ek complete standalone hook paragraph ho (130-155 characters exactly) jisme main keyword ho aur reader ko turant grab kare. Yeh line ka DOUBLE ROLE hai — (1) reader ka attention (2) Google/Facebook/Twitter ka meta description jo social share aur search preview pe dikhega. Isliye ise SELF-CONTAINED, engaging, aur keyword-rich rakho. Example: "React kya hai aur beginners kyun sikhein? Is Hindi guide me components, JSX, state aur hooks step-by-step aasan bhasha me seekho."
    - HOOK INTRO: Uske baad 2-3 lines ka relatable problem/sawaal se main content start karo. Boring definition se shuru मत karो.
    - QUICK ANSWER BOX: Intro ke turant baad ek highlighted box do jo main sawaal ka seedha jawab sirf 40-60 words mein de (Google featured snippet / position #0 ke liye). Is exact format mein:
      <div style="background:#ecfeff;border-left:4px solid #06b6d4;padding:14px 18px;border-radius:0 10px 10px 0;margin:18px 0;"><strong>⚡ Quick Answer:</strong> [40-60 word direct answer jisme main keyword ho]</div>
    - PRIMARY KEYWORD: Main keyword (topic) ko first 100 words mein zaroor use karo, aur poore article mein naturally 4-6 baar (keyword stuffing mat karo).
    - HEADINGS AS QUESTIONS: <h2> headings ko asli search questions ki tarah likho jo log Google par type karte hain (jaise "[Topic] क्या है?", "[Topic] कैसे काम करता है?", "[Topic] का use कब करें?", "[Topic] vs [Alternative] में difference?").
    - COMPARISON TABLE: Jahan possible ho, ek clean HTML <table> do (A vs B ya features) — Google tables ko featured snippet mein dikhata hai.
    - **ARCHITECTURE / FLOW DIAGRAM (jab relevant ho — REQUIRED for architectural concepts):** Agar topic architecture/flow/pattern-related ho (jaise Component Tree, State Flow, Router structure, HOC pattern, Data Fetching flow, Redux flow, Server-Client architecture, MERN stack, useEffect lifecycle, etc.), to ek visual diagram ZAROOR do using inline HTML/CSS. NO external images. Use this exact structure:
      <div style="background:#0d1b2a;border-radius:14px;padding:24px;margin:24px 0;color:#e2e8f0;text-align:center;font-family:'JetBrains Mono',monospace;">
        <div style="color:#67e8f9;font-weight:700;margin-bottom:14px;font-family:inherit;font-size:14px;text-transform:uppercase;letter-spacing:1px">🏗️ Architecture Diagram</div>
        <div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;align-items:center;">
          <div style="background:#06b6d4;color:#fff;padding:12px 20px;border-radius:10px;font-weight:600;box-shadow:0 4px 12px rgba(6,182,212,0.4)">Component A</div>
          <div style="color:#67e8f9;font-size:20px;font-weight:700">→</div>
          <div style="background:#2563eb;color:#fff;padding:12px 20px;border-radius:10px;font-weight:600;box-shadow:0 4px 12px rgba(37,99,235,0.4)">Component B</div>
          <div style="color:#67e8f9;font-size:20px;font-weight:700">→</div>
          <div style="background:#8b5cf6;color:#fff;padding:12px 20px;border-radius:10px;font-weight:600;box-shadow:0 4px 12px rgba(139,92,246,0.4)">Result</div>
        </div>
        <div style="margin-top:12px;color:#94a3b8;font-size:13px;font-style:italic">Diagram: [topic ka short flow description]</div>
      </div>
      Adapt karo (boxes, arrows, colors — cyan/blue/purple palette) topic ke hisaab se. Non-architectural topics (jaise "kya hai" definitions ya "syntax") mein diagram optional/skip.
    - STEP-BY-STEP: "Kaise karein" wale parts ko numbered <ol><li> steps mein do.
    - AUTHORITY LINK: Sirf ek external link official documentation ka do (React/Node/MDN docs jaisa) rel="noopener" aur target="_blank" ke saath — E-E-A-T trust signal ke liye.
    - SCANNABLE: Chhote paragraphs (2-3 lines max), bullet points, bold important words — mobile par easily padha jaaye, bounce rate kam ho.

    SEO & Internal Linking Requirements:
    - Automatically create internal links pointing to relevant categories on our blog by wrapping appropriate keywords in the text with <a> HTML tags.
    - Use the following specific links for labels/categories:
      - For ReactJS topics, link keywords like "ReactJS" or "React components" to: https://itinfohubs.blogspot.com/search/label/ReactJS
      - For Next.js topics, link keywords like "Next.js" or "NextJS" to: https://itinfohubs.blogspot.com/search/label/NextJS
      - For NodeJS topics, link keywords like "NodeJS" or "Runtime" to: https://itinfohubs.blogspot.com/search/label/NodeJS
      - For ExpressJS topics, link keywords like "ExpressJS" or "Middleware" to: https://itinfohubs.blogspot.com/search/label/ExpressJS
      - For MongoDB topics, link keywords like "MongoDB" or "Database" to: https://itinfohubs.blogspot.com/search/label/MongoDB
      - For general MERN Stack topics, link keywords like "MERN Stack" to: https://itinfohubs.blogspot.com/search/label/MERN%20Stack
      - For Error Solving/fixing errors, link keywords like "error", "exception", or "fix error" to: https://itinfohubs.blogspot.com/search/label/Error%20Solving
    - Do not make all keywords links. Only add 3-5 natural internal links across the entire article where it makes absolute sense.
    
    Privacy & Security Requirements:
    - Do NOT include any real or placeholder personal contact information, phone numbers, or email addresses in the article content (e.g. do not write mock contact forms, mock config files with personal email fields, or placeholder phone numbers). Keep all codes and examples completely neutral and clean.
    
    Structure & HTML Requirements:
    - Output the blog post in raw HTML format.
    - Use clean HTML tags: <h2>, <h3>, <p>, <ul>, <li>, <strong>, <a>.
    - Format code blocks using: <pre><code>[YOUR CODE HERE]</code></pre>
    - Add a key takeaways or summary block at the end (write in a friendly way, e.g. "Toh dosto, humne aaj seekha...").
    - **FAQ Accordion Section:** Add an FAQ section with 5 detailed questions and answers (real "People Also Ask" style questions that users actually search on Google).
      - IMPORTANT: DO NOT use inline styles or hardcoded colors. Use the theme's CSS classes so it looks perfect in BOTH dark AND light mode.
      - Use this EXACT format (no inline style attribute anywhere):
      <div class="faq-accordion">
        <h3 class="faq-h"><i class="fa-solid fa-circle-question"></i> Frequently Asked Questions (FAQs)</h3>
        <div class="faq-q">Q1: Question text?</div>
        <div class="faq-a">Detailed answer in Hindi/Hinglish explaining the concept clearly.</div>
        <div class="faq-q">Q2: Second question?</div>
        <div class="faq-a">Second answer.</div>
        (isi tarah total 5 question/answer pairs)
      </div>

    - **Google FAQ Schema Markup:** In addition to the visible accordion, include a JSON-LD FAQ Schema script tag at the bottom of the HTML, containing the same 5 questions and answers. Format:
      <script type="application/ld+json">
      {{
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
          {{
            "@type": "Question",
            "name": "Q1 text?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Answer text..."
            }}
          }}
        ]
      }}
      </script>
      
    Output ONLY the valid HTML content. Do not wrap the HTML in backticks (```html ... ```). Just output the raw HTML starting with the post content.
    """
    
    article_html = call_gemini(gemini_key, prompt)
    if article_html:
        # Clean up potential markdown formatting backticks
        if article_html.startswith("```html"):
            article_html = article_html[7:]
        elif article_html.startswith("```"):
            article_html = article_html[3:]
        if article_html.endswith("```"):
            article_html = article_html[:-3]
        article_html = article_html.strip()
        
        # Balance HTML tags to prevent SAXParseException XML issues
        article_html = fix_html_tags(article_html)
        
        # Banner image prepended to the post content (hidden via theme CSS in post body, used by Blogger for featuredImage)
        image_html = f'<div class="techit-hero-banner" style="text-align: center; margin-bottom: 24px;"><img src="{banner_url}" alt="{topic}" style="width: 100%; max-width: 800px; height: auto; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.15);" /></div>\n'
        full_html = image_html + article_html
        return full_html
        
    return None

def generate_seo_description(gemini_key, topic):
    print(f"[INFO] SEO search description generate kiya ja raha hai...")
    prompt = f"""
    Create a highly engaging, SEO-optimized search description for a blog post titled: "{topic}".
    The description must be in Hindi (mixed with English tech terms), extremely natural, and strictly between 120 and 150 characters (including spaces).
    Output ONLY the description text. Do not write any labels, introduction, or quotes.
    """
    desc = call_gemini(gemini_key, prompt)
    if desc:
        return desc.strip().replace('"', '')
    return f"Sikhiye {topic} ke baare me sab kuch detail me. Code, explanations aur best practices ke saath simple Hindi me tutorial."

def submit_to_indexnow(post_url):
    # Google ne purana sitemap-ping endpoint (June 2023) band kar diya, isliye ab IndexNow use karte hain.
    # IndexNow se Bing, Yandex aur DuckDuckGo ko URL turant index ke liye notify hota hai. (Free, no auth)
    if not post_url or "http" not in post_url:
        print("[INFO] IndexNow skip — koi valid live URL nahi (draft post).")
        return
    indexnow_key = os.environ.get("INDEXNOW_KEY", INDEXNOW_KEY_DEFAULT)
    host = "itinfohubs.blogspot.com"
    # No keyLocation needed — key is verified via Bing Webmaster Tools for this site.
    payload = {
        "host": host,
        "key": indexnow_key,
        "urlList": [post_url, f"https://{host}/sitemap.xml"]
    }
    # Bing IndexNow endpoint (shared with Yandex/DuckDuckGo via the IndexNow protocol)
    for endpoint in ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow"]:
        try:
            res = requests.post(endpoint, json=payload, timeout=15,
                                headers={"Content-Type": "application/json; charset=utf-8"})
            if res.status_code in (200, 202):
                print(f"[SUCCESS] IndexNow submitted to {endpoint} (status {res.status_code}) — Bing/Yandex jaldi index karenge.")
                return
            else:
                print(f"[INFO] IndexNow {endpoint} returned {res.status_code}: {res.text[:120]}")
        except Exception as e:
            print(f"[WARNING] IndexNow {endpoint} failed: {e}")


def _get_indexing_credentials():
    # Google Indexing API ke liye service account credentials (env JSON ya local file se).
    from google.oauth2 import service_account
    sa_info = None
    env_sa = os.environ.get("GOOGLE_INDEXING_SA", "").strip()
    if env_sa:
        try:
            sa_info = json.loads(env_sa)
        except Exception as e:
            print(f"[WARNING] GOOGLE_INDEXING_SA env parse failed: {e}")
    elif os.path.exists("google_indexing_sa.json") and os.path.getsize("google_indexing_sa.json") > 0:
        try:
            with open("google_indexing_sa.json", "r", encoding="utf-8") as f:
                sa_info = json.load(f)
        except Exception as e:
            print(f"[WARNING] google_indexing_sa.json parse failed: {e}")
    if not sa_info:
        return None
    try:
        return service_account.Credentials.from_service_account_info(
            sa_info, scopes=["https://www.googleapis.com/auth/indexing"])
    except Exception as e:
        print(f"[WARNING] Indexing credentials build failed: {e}")
        return None


def submit_to_google_indexing(post_url):
    # Google Indexing API ko notify karo taaki naya post jaldi crawl/index ho.
    if not post_url or "http" not in post_url:
        return False
    creds = _get_indexing_credentials()
    if not creds:
        print("[INFO] Google Indexing skip — service account configured nahi (GOOGLE_INDEXING_SA).")
        return False
    try:
        from google.auth.transport.requests import Request as GRequest
        creds.refresh(GRequest())
        headers = {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}
        body = {"url": post_url, "type": "URL_UPDATED"}
        r = requests.post("https://indexing.googleapis.com/v3/urlNotifications:publish",
                          headers=headers, json=body, timeout=20)
        if r.status_code == 200:
            print(f"[SUCCESS] Google Indexing API submitted: {post_url}")
            return True
        print(f"[INFO] Google Indexing returned {r.status_code}: {r.text[:160]}")
    except Exception as e:
        print(f"[WARNING] Google Indexing submit failed: {e}")
    return False


def notify_telegram(text, silent=False):
    # Telegram par message bhejta hai. Token/chat-id na ho to chup-chaap skip (kuch break nahi hota).
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return False  # Telegram configured nahi hai — gracefully skip
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        res = requests.post(url, timeout=15, data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "false",
            "disable_notification": "true" if silent else "false"
        })
        if res.status_code == 200:
            print("[SUCCESS] Telegram notification sent.")
            return True
        print(f"[WARNING] Telegram returned {res.status_code}: {res.text[:150]}")
    except Exception as e:
        print(f"[WARNING] Telegram notify failed: {e}")
    return False


def share_post_to_telegram(title, post_url, category, seo_desc):
    # Naya LIVE post Telegram channel par auto-share — traffic ke liye.
    clean_title = title.replace("(In Hindi)", "").replace("(in Hindi)", "").strip()
    msg = (
        f"🚀 <b>New Post Live!</b>\n\n"
        f"📝 <b>{clean_title}</b>\n\n"
        f"{seo_desc}\n\n"
        f"🏷 {category}\n"
        f"🔗 <a href='{post_url}'>Abhi padho →</a>\n\n"
        f"#TechIT #{category.replace(' ', '')} #Coding"
    )
    return notify_telegram(msg)

def publish_to_blogger(title, html_content, category, is_draft=True, seo_description=None):
    print("[INFO] Blogger API authenticate kiya ja raha hai...")
    
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"[ERROR] Credentials file '{CREDENTIALS_FILE}' nahi mili.")
        print("Pehle setup_blogger_api.py run karke credentials authorization generate karein.")
        return False
        
    try:
        if os.path.getsize(CREDENTIALS_FILE) == 0:
            print(f"[ERROR] Credentials file '{CREDENTIALS_FILE}' empty (khali) hai. GitHub Secrets me BLOGGER_CREDENTIALS_JSON ki value sahi se paste karein.")
            return False
            
        with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print(f"[ERROR] Credentials file '{CREDENTIALS_FILE}' khali hai.")
                return False
            creds_data = json.loads(content)
            
        creds = Credentials(
            token=None,
            refresh_token=creds_data['refresh_token'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            token_uri=creds_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            scopes=creds_data['scopes']
        )
        
        # Refresh the credentials token using Request object
        creds.refresh(Request())
        
        # Build the blogger API v3 client
        service = build('blogger', 'v3', credentials=creds)
        
        # Insert post parameters
        labels = [category, "MERN Stack", "Coding info"]
        post_body = {
            "kind": "blogger#post",
            "blog": {"id": BLOG_ID},
            "title": title,
            "content": html_content,
            "labels": labels
        }
        # IMAGES field — Blogger ko force karo direct ImgBB URL use kare (proxy resize bacha).
        # Content me first <img> ka src nikaal ke images metadata me set karo.
        import re as _re
        _img_match = _re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html_content)
        if _img_match:
            _img_url = _img_match.group(1)
            post_body["images"] = [{"url": _img_url}]

        # META DESCRIPTION — 3 tareeke se unique per post ensure karo:
        # (1) customMetaData JSON (future theme use), (2) searchDescription Blogger field,
        # (3) visible SEO intro paragraph — theme ka JS content-snippet isko pick karega,
        #     og:description bhi unique hoga, aur reader ke liye bhi TL;DR banega.
        if seo_description:
            desc_clean = seo_description.strip()
            desc = desc_clean[:160]
            post_body["customMetaData"] = json.dumps({"description": desc})
            # Blogger ka apna searchDescription field — sometimes accepted
            post_body["searchDescription"] = desc

            # Visible SEO intro paragraph — banner ke turant baad prepend
            intro_html = (
                f'<p class="techit-seo-intro" style="font-size:1.05em;line-height:1.7;'
                f'color:#0d1b2a;padding:14px 18px;background:linear-gradient(to right,#ecfdff,#f0f9ff);'
                f'border-left:4px solid #06b6d4;border-radius:8px;margin:8px 0 24px 0;">'
                f'<strong style="color:#06b6d4;">✨ Quick Answer:</strong> {desc_clean}</p>\n'
            )
            # Banner div ke andar mat daalo — uske BAAD daalo
            banner_marker = 'techit-hero-banner'
            if banner_marker in html_content[:600]:
                # Banner div ka closing </div> dhundo
                banner_start = html_content.find(banner_marker)
                div_end = html_content.find('</div>', banner_start)
                if div_end != -1:
                    insert_pos = div_end + len('</div>')
                    # newline agla ho to skip
                    if insert_pos < len(html_content) and html_content[insert_pos] == '\n':
                        insert_pos += 1
                    html_content = html_content[:insert_pos] + intro_html + html_content[insert_pos:]
                else:
                    html_content = intro_html + html_content
            else:
                html_content = intro_html + html_content
            # post_body me updated content set karo
            post_body["content"] = html_content
        
        print(f"[INFO] Blog Post ko Blogger par upload kiya ja raha hai ({'Draft' if is_draft else 'Live'})...")
        
        posts_service = service.posts()
        request = posts_service.insert(
            blogId=BLOG_ID,
            body=post_body,
            isDraft=is_draft
        )
        response = request.execute()
        
        print("\n[SUCCESS] Post successfully uploaded to Blogger!")
        print(f"Title: {response['title']}")
        print(f"Post URL: {response.get('url', 'URL is generated when published')}")
        print(f"Status: {response['status']}")
        # Return URL on success (live posts have a public url; drafts return empty string)
        return {"success": True, "url": response.get("url", ""), "status": response.get("status", "")}

    except Exception as e:
        print(f"[ERROR] Blogger API call failed: {e}")
        return {"success": False, "url": "", "status": "error"}

def fetch_live_post_titles():
    print("[INFO] Blogger se live post titles fetch kiye ja rahe hain duplicate check karne ke liye...")
    if not os.path.exists(CREDENTIALS_FILE):
        return []
        
    try:
        if os.path.getsize(CREDENTIALS_FILE) == 0:
            return []
            
        with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            creds_data = json.loads(content)
            
        creds = Credentials(
            token=None,
            refresh_token=creds_data['refresh_token'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            token_uri=creds_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            scopes=creds_data['scopes']
        )
        
        creds.refresh(Request())
        service = build('blogger', 'v3', credentials=creds)
        
        # Get last 50 posts to prevent duplicates
        posts_data = service.posts().list(blogId=BLOG_ID, view='AUTHOR', maxResults=50).execute()
        titles = []
        if 'items' in posts_data:
            for post in posts_data['items']:
                # Clean up suffixes like "(In Hindi)" or "(in Hindi)"
                title = post['title'].replace("(In Hindi)", "").replace("(in Hindi)", "").strip()
                titles.append(title)
        print(f"[OK] Blogger live posts se {len(titles)} titles fetch kiye gaye.")
        return titles
    except Exception as e:
        print(f"[WARNING] Live post titles fetch failed: {e}")
        return []

def ask_user_for_topic(gemini_key, posted_topics):
    """
    Jab script locally run ho, user se topic poochhe.
    Agar kuch nahi diya (Enter press kiya) toh auto-select karo.
    """
    print("\n==================================================")
    print("  BLOG TOPIC SELECTION")
    print("==================================================")
    print("Aap apna khud ka topic de sakte hain, ya Enter press karein")
    print("aur system automatically ek naya topic choose karega.")
    print("--------------------------------------------------")
    print("Examples:")
    print("  > React Query vs SWR: Data Fetching Comparison")
    print("  > MongoDB Transactions aur ACID Properties")
    print("  > NodeJS Worker Threads for CPU-heavy tasks")
    print("--------------------------------------------------")
    
    try:
        user_topic = input("\nApna blog topic enter karein (ya sirf Enter dabao auto ke liye): ").strip()
    except (EOFError, KeyboardInterrupt):
        user_topic = ""
    
    if user_topic:
        print(f"\n[OK] Aapka topic: '{user_topic}'")
        print("[INFO] Category classify kiya ja raha hai...")
        category = classify_topic_category(gemini_key, user_topic)
        print(f"[OK] Category: {category}")
        return user_topic, category
    else:
        print("\n[INFO] Koi topic nahi diya. Auto-select mode...")
        return select_topic(gemini_key, posted_topics)


def _extract_first_image(html):
    # Post HTML se pehli image ka URL nikalo (Pinterest pin ke liye banner chahiye).
    if not html:
        return ""
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html)
    return m.group(1) if m else ""


def write_preview_file(title, category, seo_desc, content_html):
    # Local preview.html generate karta hai testing/checking ke liye.
    try:
        preview_file = "preview.html"
        with open(preview_file, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Preview: {title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; background: #0a1320; color: #e8eef8; }}
        img {{ max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); }}
        pre {{ background: #0f1d30; padding: 16px; border-radius: 8px; overflow-x: auto; color: #f8fafc; border: 1px solid #1f3550; }}
        code {{ font-family: monospace; }}
        a {{ color: #06b6d4; text-decoration: none; }}
        details {{ background: #13243a; padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #1f3550; }}
    </style>
</head>
<body>
    <div style="background: #13243a; padding: 18px; border-radius: 12px; border: 1px solid #06b6d4; margin-bottom: 24px;">
        <h3 style="margin-top:0; color:#06b6d4; font-size:16px;">📋 Blogger Search Description (Click to Copy):</h3>
        <textarea style="width:100%; height:60px; background:#0a1320; color:#e8eef8; border:1px solid #1f3550; border-radius:6px; padding:8px; box-sizing:border-box; font-family:inherit; font-size:14px; resize:none;" readonly onclick="this.select(); document.execCommand('copy'); alert('Copied to clipboard!');">{seo_desc}</textarea>
        <p style="margin:6px 0 0 0; font-size:12px; color:#8195b2;">Copy and paste this in the "Search Description" section of the Blogger post editor sidebar before publishing.</p>
    </div>
    <h1>{title}</h1>
    <p><strong>Category:</strong> {category}</p>
    <hr style="border: 0; border-top: 1px solid #1f3550; margin: 20px 0;">
    {content_html}
</body>
</html>""")
        print(f"[OK] Local HTML preview file generated: '{preview_file}'")
    except Exception as e:
        print(f"[WARNING] Failed to generate preview file: {e}")


def create_one_post(gemini_key, posted_topics, is_interactive, is_draft):
    """Ek post generate + publish karta hai. Success par True return, fail par False."""
    # 1. Select Topic — interactive mein user se poochho, warna auto
    if is_interactive:
        topic, category = ask_user_for_topic(gemini_key, posted_topics)
    else:
        topic, category = select_topic(gemini_key, posted_topics)

    # 2. Generate Content
    # Bug fix: agar topic me pehle se "(in Hindi)" hai to dobara mat lagao (title duplicate se bacha)
    _topic_lower = topic.lower()
    if "(in hindi)" in _topic_lower or "(in hindi )" in _topic_lower:
        title = topic  # already has it
    else:
        title = f"{topic} (In Hindi)"

    # SEO: Google search me sirf ~60 chars dikhta hai — usse zyada trim karo taaki
    # snippet me title poori dikhe aur click-through rate badhe.
    if len(title) > 60:
        # Pehle "(In Hindi)" hata do agar exists, phir title trim karo, phir "(Hindi)" chhota add karo
        base = re.sub(r'\s*\((?:in|In)\s*[Hh]indi\)\s*$', '', title).strip()
        if len(base) > 52:
            # 52 chars me trim, saf shabd tak
            base = base[:52].rsplit(' ', 1)[0] if ' ' in base[:52] else base[:52]
        title = f"{base} (Hindi)"
        print(f"[INFO] Title trimmed to fit Google (~60 chars): \"{title}\"")
    print(f"\n[INFO] Blog generate ho raha hai: \"{title}\"")
    content_html = generate_article_content(gemini_key, topic, category)
    if not content_html:
        print("[ERROR] Article content generate nahi ho paya. Is post ko skip kar rahe hain.")
        return False

    # 3. SEO description + local preview
    seo_desc = generate_seo_description(gemini_key, topic)
    print(f"[OK] Generated Search Description: {seo_desc}")
    write_preview_file(title, category, seo_desc, content_html)

    # 4. Interactive single run mein draft/live choice
    if is_interactive:
        print("\n--------------------------------------------------")
        print("Publishing Settings:")
        print("1. Draft mode me save karein (Recommended - Blogger dashboard se check karke live karein)")
        print("2. Direct Live Publish kar dein")
        try:
            choice = input("Enter choice (1 or 2, default 1): ").strip()
            if choice == "2":
                is_draft = False
                confirm = input(f"Confirm: '{title}' ko LIVE publish karna chahte ho? (yes/no): ").strip().lower()
                if confirm not in ("yes", "y", "ha", "han"):
                    is_draft = True
                    print("[INFO] Cancelled. Draft mode mein save ho raha hai.")
        except (EOFError, KeyboardInterrupt):
            print("[INFO] Input skipped. Defaulting to Draft mode.")

    # 5. Publish
    result = publish_to_blogger(title, content_html, category, is_draft=is_draft, seo_description=seo_desc)
    if not result.get("success"):
        notify_telegram(f"⚠️ <b>TechIT Auto-Blogger</b>\nPost publish FAIL hui: <b>{title}</b>\nLogs check karein.")
        return False

    # 6. Post-publish automations
    save_posted_topic(topic)
    posted_topics.append(topic)  # in-memory list update — loop ke agle post mein duplicate na ho
    post_url = result.get("url", "")

    if not is_draft and post_url:
        # Live post — instant index (Google + Bing/Yandex) + social share
        submit_to_google_indexing(post_url)
        submit_to_indexnow(post_url)
        share_post_to_telegram(title, post_url, category, seo_desc)
        # Multi-platform auto-share (Twitter/X, Facebook, Pinterest) — banner image bhi bhejte hain
        clean_title = title.replace("(In Hindi)", "").replace("(in Hindi)", "").strip()
        image_url = _extract_first_image(content_html)
        shared = social_share.share_all(clean_title, post_url, category, seo_desc, image_url)
        if shared:
            notify_telegram(f"📣 <b>{clean_title}</b>\nShare hua: {', '.join(shared)}", silent=True)
        # Cross-post to Dev.to / Hashnode for backlinks (gated on tokens)
        try:
            xp = cross_post.cross_post_all(clean_title, content_html, post_url, category)
            if xp:
                notify_telegram(f"🔗 <b>{clean_title}</b>\nCross-post (backlinks): {', '.join(xp)}", silent=True)
        except Exception as ex:
            print(f"[WARNING] Cross-post error: {ex}")
    else:
        # Draft — sirf notify (URL public nahi hota)
        notify_telegram(f"📝 <b>TechIT</b>: Naya DRAFT ready — <b>{title}</b>\nBlogger dashboard se review karke live karein.", silent=True)

    print("==================================================")
    print(f"[SUCCESS] Post done: '{topic}'")
    print("==================================================")
    return True


def main():
    print("==================================================")
    print("  TechIT Auto-Blogger - Powered by Gemini AI  ")
    print("==================================================")

    try:
        gemini_key = load_gemini_api_key()
        posted_topics = get_posted_topics()

        # COOLDOWN CHECK — hourly schedule ke saath 30 min cooldown (accidental double-fire se bacha).
        # Manual dispatch: SKIP_COOLDOWN=true set karke bypass kar sakte hain.
        skip_cooldown = os.environ.get("SKIP_COOLDOWN", "false").lower() == "true"
        is_manual = os.environ.get("GITHUB_EVENT_NAME", "") == "workflow_dispatch"
        if not skip_cooldown and not is_manual:
            try:
                r = requests.get("https://itinfohubs.blogspot.com/feeds/posts/default?alt=json&max-results=1", timeout=20)
                if r.ok:
                    latest = r.json().get("feed", {}).get("entry", [{}])[0]
                    pub = latest.get("published", {}).get("$t", "")
                    if pub:
                        import datetime
                        pub_dt = datetime.datetime.fromisoformat(pub.replace("Z", "+00:00"))
                        now_dt = datetime.datetime.now(datetime.timezone.utc)
                        hours = (now_dt - pub_dt).total_seconds() / 3600
                        if hours < 0.5:
                            print(f"[COOLDOWN] Last post sirf {hours*60:.0f} min pehle hua — hourly slot double-fire se bacha rahe hain, skip.")
                            print("           Manually run karna ho to workflow_dispatch use karo ya SKIP_COOLDOWN=true.")
                            return
                        print(f"[OK] Last post {hours:.1f} ghante pehle — cooldown clear, aage badho.")
            except Exception as e:
                print(f"[WARN] Cooldown check fail (aage badh rahe hain): {e}")

        # Live fetch posts to avoid duplicates 100%
        live_titles = fetch_live_post_titles()
        if live_titles:
            posted_topics = list(set(posted_topics + live_titles))

        is_interactive = sys.stdin.isatty() and not os.environ.get("GITHUB_ACTIONS")

        # Draft vs Live decide karo
        if is_interactive:
            is_draft = True  # interactive run create_one_post ke andar khud poochhega
        else:
            env_live = os.environ.get("PUBLISH_LIVE", "false").lower() == "true"
            is_draft = not env_live
            print(f"[INFO] Non-interactive execution. Post status: {'Draft' if is_draft else 'Live'}")

        # Kitne posts banane hain — POSTS_PER_RUN env (default 1)
        try:
            posts_per_run = max(1, int(os.environ.get("POSTS_PER_RUN", "1")))
        except ValueError:
            posts_per_run = 1
        if is_interactive:
            posts_per_run = 1  # interactive mein hamesha 1 post
        print(f"[INFO] Is run mein {posts_per_run} post(s) banaye jayenge.")

        made = 0
        for i in range(posts_per_run):
            if posts_per_run > 1:
                print(f"\n############## POST {i + 1} / {posts_per_run} ##############")
            if create_one_post(gemini_key, posted_topics, is_interactive, is_draft):
                made += 1
            if i < posts_per_run - 1:
                time.sleep(5)  # API rate-limit ke liye chhota gap

        if made == 0:
            print("[ERROR] Koi post publish nahi hui. Logs check karein.")
            notify_telegram("🚨 <b>TechIT Auto-Blogger</b>\nAaj koi bhi post publish nahi hui! Logs check karein.")
            sys.exit(1)

        print(f"\n[SUCCESS] Process complete — {made}/{posts_per_run} post(s) publish/draft hue.")

    except SystemExit:
        raise
    except Exception as e:
        # Koi bhi unexpected crash — Telegram par alert bhejo, taaki silent fail na ho
        print(f"[FATAL] Script crashed: {e}")
        notify_telegram(f"🚨 <b>TechIT Auto-Blogger CRASH</b>\n<code>{str(e)[:300]}</code>")
        sys.exit(1)


if __name__ == '__main__':
    main()
