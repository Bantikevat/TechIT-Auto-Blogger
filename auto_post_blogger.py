import os
import json
import sys
import random
import urllib.parse
import requests
import time

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


# Default topics to fallback on
DEFAULT_TOPICS = [
    {"topic": "React Context API Tutorial in Hindi", "category": "ReactJS"},
    {"topic": "NodeJS Event Loop and Thread Pool explained", "category": "NodeJS"},
    {"topic": "MongoDB Aggregation Pipeline ($group, $match, $lookup)", "category": "MongoDB"},
    {"topic": "ExpressJS Custom Middleware Architecture", "category": "ExpressJS"},
    {"topic": "JWT Authentication with Access and Refresh Tokens in MERN Stack", "category": "MERN Stack"},
    {"topic": "React Hooks: Custom useFetch Hook implementation", "category": "ReactJS"},
    {"topic": "NodeJS Streams and Buffers for high performance", "category": "NodeJS"},
    {"topic": "MongoDB Indexing and Query Performance Optimization", "category": "MongoDB"},
    {"topic": "Error Handling best practices in Express JS", "category": "ExpressJS"},
    {"topic": "React performance optimization using useMemo and useCallback", "category": "ReactJS"}
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
    models = ["gemini-3.5-flash", "gemini-3.1-flash-lite"]
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
        # Try up to 2 times for each model in case of temporary 503s
        for attempt in range(2):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    res_json = response.json()
                    text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                    return text
                elif response.status_code in [503, 429]:
                    print(f"[WARNING] Gemini model {model} returned {response.status_code} (attempt {attempt+1}/2). Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print(f"[WARNING] Gemini model {model} returned status code {response.status_code}: {response.text}. Trying next option.")
                    break # Break out of attempt loop to try the next model
            except Exception as e:
                print(f"[WARNING] Error calling Gemini model {model}: {e}")
                time.sleep(2)
                
    return None

def classify_topic_category(gemini_key, topic):
    # Quick call to Gemini to classify the topic's category
    prompt = f"""
    Classify this programming tutorial topic: "{topic}"
    Choose EXACTLY one category from this list: ReactJS, NodeJS, ExpressJS, MongoDB, MERN Stack.
    Output ONLY the category name (just a single word from the list). Do not output any other text or explanation.
    """
    category = call_gemini(gemini_key, prompt)
    if category:
        category = category.strip()
        # Clean up response
        for valid in ["ReactJS", "NodeJS", "ExpressJS", "MongoDB", "MERN Stack"]:
            if valid.lower() in category.lower():
                return valid
    return "MERN Stack" # Default fallback

def select_topic(gemini_key, posted_topics):
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
    
    prompt = f"""
    You are an expert programming blogger. Choose one unique, highly educational, and trending web development topic focusing on MERN stack (MongoDB, Express, React, Node.js) or modern JavaScript.
    The topic must NOT be in this list of already written topics: {posted_topics}.
    
    Output ONLY a JSON object containing the topic title and the category (which must be exactly one of: ReactJS, NodeJS, ExpressJS, MongoDB, or MERN Stack).
    Do not output any markdown formatting, backticks, or comments. Just raw JSON.
    Example output format:
    {{"topic": "React Context API vs Redux in 2026", "category": "ReactJS"}}
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
            print(f"[OK] Gemini dynamically selected topic: '{data['topic']}' (Category: {data['category']})")
            return data["topic"], data["category"]
        except Exception as e:
            print(f"[WARNING] Failed to parse Gemini response: {e}")
            
    # Fallback to defaults
    available = [t for t in DEFAULT_TOPICS if t["topic"] not in posted_topics]
    if not available:
        available = DEFAULT_TOPICS
        
    choice = random.choice(available)
    print(f"[OK] Selected fallback topic: '{choice['topic']}' (Category: {choice['category']})")
    return choice["topic"], choice["category"]

def generate_image_prompt(gemini_key, topic):
    print(f"[INFO] Image prompt generate kiya ja raha hai for: '{topic}'...")
    # Clean topic for image text to make it short and clean
    clean_topic = topic.replace("(In Hindi)", "").replace("(in Hindi)", "").strip()
    
    prompt = f"""
    Create a highly descriptive and creative English image prompt for a blog post banner related to: "{clean_topic}".
    Describe a beautiful, modern, high-quality tech digital illustration (flat vector or 3D render style) with a dark theme, neon colors (cyan, purple, green).
    The image MUST contain the text "{clean_topic}" written in a very clean, readable, bold, modern neon sans-serif font, centered as a prominent title on the graphic, looking like a professional YouTube thumbnail or blog banner.
    Output ONLY the one-sentence prompt. Do not output anything else.
    """
    custom_prompt = call_gemini(gemini_key, prompt)
    if custom_prompt:
        custom_prompt = custom_prompt.strip().replace('"', '').replace('\n', ' ')
        return f"{custom_prompt}, ultra-detailed, modern tech style, dark mode neon, high contrast, visually attractive, clean typography"
    return f"Modern flat vector tech illustration for {clean_topic} with bold readable text '{clean_topic}', neon colors, dark tech background, clean typography"

def generate_article_content(gemini_key, topic, category):
    print(f"[INFO] Article content generate kiya ja raha hai for: '{topic}'...")
    
    # 1. Generate customized image prompt dynamically using Gemini
    custom_prompt = generate_image_prompt(gemini_key, topic)
    print(f"[OK] Generated custom image prompt: '{custom_prompt}'")
    
    # Generate clean banner image using pollinations
    banner_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(custom_prompt)}?width=800&height=450&nologo=true"
    
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
    
    SEO & Internal Linking Requirements:
    - Automatically create internal links pointing to relevant categories on our blog by wrapping appropriate keywords in the text with <a> HTML tags.
    - Use the following specific links for labels/categories:
      - For ReactJS or frontend topics, link keywords like "ReactJS" or "React components" to: https://itinfohubs.blogspot.com/search/label/ReactJS
      - For NodeJS topics, link keywords like "NodeJS" or "Runtime" to: https://itinfohubs.blogspot.com/search/label/NodeJS
      - For ExpressJS topics, link keywords like "ExpressJS" or "Middleware" to: https://itinfohubs.blogspot.com/search/label/ExpressJS
      - For MongoDB topics, link keywords like "MongoDB" or "Database" to: https://itinfohubs.blogspot.com/search/label/MongoDB
      - For general MERN Stack topics, link keywords like "MERN Stack" to: https://itinfohubs.blogspot.com/search/label/MERN%20Stack
    - Do not make all keywords links. Only add 3-5 natural internal links across the entire article where it makes absolute sense.
    
    Structure & HTML Requirements:
    - Output the blog post in raw HTML format.
    - Use clean HTML tags: <h2>, <h3>, <p>, <ul>, <li>, <strong>, <a>.
    - Format code blocks using: <pre><code>[YOUR CODE HERE]</code></pre>
    - Add a key takeaways or summary block at the end (write in a friendly way, e.g. "Toh dosto, humne aaj seekha...").
    - **FAQ Accordion Section:** Add an FAQ section with 3 detailed questions and answers using the HTML <details> and <summary> tags. Format it like this:
      <div class="faq-accordion">
        <h3>Frequently Asked Questions (FAQs)</h3>
        <details style="background: #1e293b; color: #f1f5f9; padding: 12px; border: 1px solid #334155; border-radius: 8px; margin-bottom: 10px; cursor: pointer;">
          <summary style="font-weight: bold; font-size: 15px;">Q1: Question text?</summary>
          <p style="margin-top: 8px; color: #cbd5e1; line-height: 1.6;">Detailed answer explaining the concept...</p>
        </details>
      </div>
      
    - **Google FAQ Schema Markup:** In addition to the visible accordion, include a JSON-LD FAQ Schema script tag at the bottom of the HTML, containing the same 3 questions and answers. Format:
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
        
        # Prepended banner image to the post content
        image_html = f'<div style="text-align: center; margin-bottom: 24px;"><img src="{banner_url}" alt="{topic}" style="width: 100%; max-width: 800px; height: auto; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.15);" /></div>\n'
        full_html = image_html + article_html
        return full_html
        
    return None

def publish_to_blogger(title, html_content, category, is_draft=True):
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
        return True
        
    except Exception as e:
        print(f"[ERROR] Blogger API call failed: {e}")
        return False

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

def main():
    print("==================================================")
    print("  TechIT MERN Stack Auto-Blogger  ")
    print("==================================================")
    
    gemini_key = load_gemini_api_key()
    posted_topics = get_posted_topics()
    
    # Live fetch posts to avoid duplicates 100%
    live_titles = fetch_live_post_titles()
    if live_titles:
        posted_topics = list(set(posted_topics + live_titles))
    
    # 1. Select Topic
    topic, category = select_topic(gemini_key, posted_topics)
    
    # 2. Generate Content
    title = f"{topic} (In Hindi)"
    content_html = generate_article_content(gemini_key, topic, category)
    
    if not content_html:
        print("[ERROR] Article content generate nahi ho paya. Script stopped.")
        sys.exit(1)
        
    # Check if running in non-interactive environment (like GitHub Actions)
    is_interactive = sys.stdin.isatty() and not os.environ.get("GITHUB_ACTIONS")
    is_draft = True
    
    if is_interactive:
        # Ask if user wants to publish as live or draft
        print("\n--------------------------------------------------")
        print("Publishing Settings:")
        print("1. Draft mode me save karein (Recommended - check karke dashboard se manually live karein)")
        print("2. Direct Publish (Live) kar dein")
        try:
            choice = input("Enter choice (1 or 2, default 1): ").strip()
            if choice == "2":
                is_draft = False
        except (EOFError, KeyboardInterrupt):
            print("[INFO] Input skipped. Defaulting to Draft mode.")
    else:
        # In non-interactive mode, check env var PUBLISH_LIVE. Default is Draft (safe)
        env_live = os.environ.get("PUBLISH_LIVE", "false").lower() == "true"
        is_draft = not env_live
        print(f"[INFO] Non-interactive execution. Post status: {'Draft' if is_draft else 'Live'}")
        
    success = publish_to_blogger(title, content_html, category, is_draft=is_draft)
    
    if success:
        # Save to posted topics track file to avoid repeating it
        save_posted_topic(topic)
        print("==================================================")
        print("[SUCCESS] Process Completed successfully!")
        print("==================================================")
    else:
        print("[ERROR] Post publish nahi ho payi. Logs check karein.")
        sys.exit(1)

if __name__ == '__main__':
    main()
