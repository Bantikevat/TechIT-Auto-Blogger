"""
gemini_tools.py — TechIT Gemini Automation Toolkit
By/for Banti Kevat (TechIT — Tech in Hindi)

3 kaam Gemini se automate karta hai:
  1. topics    -> trending blog post ideas generate karke topics_to_write.txt me add
  2. captions  -> ek post ke liye platform-wise social media captions
  3. faq       -> ek post ke liye 5 FAQ (theme ke faq-q/faq-a HTML format me)
  4. rewrite   -> kisi reference post se 100% ORIGINAL behtar post (SEO-ready HTML)

Usage:
  python gemini_tools.py topics [N]                         (default N=10)
  python gemini_tools.py captions "Post Title" "post-url"
  python gemini_tools.py faq "Post Title"
  python gemini_tools.py rewrite "reference.txt"            (reference me post copy-paste karo)

API key: GEMINI_API_KEY env var ya gemini_api_key.txt file se.
"""
import os
import sys
import json
import re
import requests

# Windows console pe Hindi/emoji/dash clean dikhe (UTF-8)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

GEMINI_KEY_FILE = "gemini_api_key.txt"
QUEUE_FILE = "topics_to_write.txt"
TRACKER_FILE = "posted_topics.json"
# auto_post_blogger.py jaise hi models (fallback chain)
MODELS = ["gemini-2.5-flash-latest", "gemini-1.5-flash", "gemini-1.5-flash-8b"]


def load_gemini_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key
    if os.path.exists(GEMINI_KEY_FILE):
        with open(GEMINI_KEY_FILE, "r", encoding="utf-8") as f:
            api_key = f.read().strip()
            if api_key:
                return api_key
    print("[ERROR] Gemini API key nahi mili (gemini_api_key.txt ya GEMINI_API_KEY env var).")
    sys.exit(1)


def ask_gemini(prompt, temperature=0.9):
    """Gemini REST call with model fallback. Text return karta hai, warna None."""
    key = load_gemini_api_key()
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        try:
            r = requests.post(url, json=payload, timeout=60)
            if r.status_code == 200:
                data = r.json()
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                except (KeyError, IndexError):
                    print(f"[WARN] {model}: empty/blocked response, next model try kar raha hoon...")
                    continue
            else:
                print(f"[WARN] {model}: HTTP {r.status_code} -> fallback")
        except Exception as e:
            print(f"[WARN] {model}: {e} -> fallback")
    return None


def _existing_topics():
    """Queue + posted history se sab known topics (lowercase) — duplicate avoid karne ke liye."""
    seen = set()
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    seen.add(line.strip().lower())
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data if isinstance(data, list) else data.values()
            for item in items:
                if isinstance(item, str):
                    seen.add(item.lower())
                elif isinstance(item, dict):
                    for v in item.values():
                        if isinstance(v, str):
                            seen.add(v.lower())
        except Exception:
            pass
    return seen


def cmd_topics(n=10):
    seen = _existing_topics()
    prompt = (
        f"Tum TechIT blog (Tech in Hindi) ke content strategist ho. "
        f"{n + 4} fresh, SEO-friendly blog post TITLE ideas do — ek Hindi/Hinglish coding blog ke liye. "
        f"Focus areas: React, Next.js, Node.js, Express, MongoDB (MERN stack), JavaScript, "
        f"AI tools, common coding errors aur unke solutions, aur tech news. "
        f"Har title catchy + search-friendly ho, aur jahan fit baithe wahan '(in Hindi)' lagao. "
        f"SIRF titles do — ek line me ek title. Numbering, bullets ya koi extra text mat do."
    )
    out = ask_gemini(prompt)
    if not out:
        print("[ERROR] Gemini se response nahi mila.")
        return
    new = []
    for line in out.splitlines():
        t = re.sub(r'^[\s\-\*\d\.\)]+', '', line).strip().strip('"')
        if t and t.lower() not in seen:
            seen.add(t.lower())
            new.append(t)
        if len(new) >= n:
            break
    if not new:
        print("Koi naya topic nahi mila (sab duplicate the). Dobara chalao.")
        return
    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        for t in new:
            f.write(t + "\n")
    print(f"[OK] {len(new)} naye topics '{QUEUE_FILE}' me add ho gaye:\n")
    for i, t in enumerate(new, 1):
        print(f"  {i}. {t}")


def cmd_captions(title, url=""):
    prompt = (
        f"Tum TechIT (Tech in Hindi) ke social media manager ho. "
        f"Niche diye post ke liye platform-wise social media captions likho.\n\n"
        f"Post title: {title}\n"
        f"Post URL: {url}\n\n"
        f"Hinglish (Hindi + English) me, engaging, emojis ke saath. "
        f"In 5 platforms ke liye ALAG-ALAG caption do, har ek apne style me:\n"
        f"1) WhatsApp/Telegram — short, friendly, 1-2 line + URL\n"
        f"2) X (Twitter) — 280 char ke andar, 2-3 hashtags\n"
        f"3) Facebook — hook + thoda detail + URL + hashtags\n"
        f"4) LinkedIn — professional, value-focused, 3-4 lines\n"
        f"5) Instagram — catchy hook + 8-10 relevant hashtags\n\n"
        f"Har platform ka naam heading ki tarah, phir uska caption. Saaf aur ready-to-paste."
    )
    out = ask_gemini(prompt, temperature=1.0)
    print("\n" + (out or "[ERROR] response nahi mila") + "\n")


def cmd_faq(title):
    prompt = (
        f"Tum TechIT (Tech in Hindi) ke SEO writer ho. "
        f"Is blog topic ke liye 5 FAQ banao: \"{title}\".\n"
        f"Questions wahi ho jo log asal me Google par search karte hain. "
        f"Answers Hinglish me, simple, 2-3 lines, genuinely helpful.\n\n"
        f"Output EXACTLY is HTML format me do (aur kuch nahi, koi markdown nahi):\n\n"
        f'<h3 class="faq-h"><i class="fa-solid fa-circle-question"></i> FAQ — Aksar Puchhe Jaane Wale Sawal</h3>\n'
        f'<div class="faq-q">Pehla sawal?</div>\n'
        f'<div class="faq-a">Pehla jawab.</div>\n'
        f"(isi tarah total 5 question/answer pairs)"
    )
    out = ask_gemini(prompt, temperature=0.7)
    print("\n" + (out or "[ERROR] response nahi mila") + "\n")
    print("--- Upar ka HTML copy karke post ke HTML view me paste karo. Theme auto accordion + FAQ schema bana dega. ---")


def cmd_rewrite(ref_file):
    if not os.path.exists(ref_file):
        print(f"[ERROR] Reference file nahi mili: {ref_file}")
        print('Pehle ek file banao (jaise reference.txt) aur usme woh post copy-paste karo jisse inspiration leni hai.')
        return
    with open(ref_file, "r", encoding="utf-8") as f:
        reference = f.read().strip()
    if len(reference) < 50:
        print("[ERROR] Reference content bahut chhota hai. Poora article paste karo.")
        return

    instructions = """Tum TechIT (Tech in Hindi) ke senior content writer ho.
Neeche ek REFERENCE article diya hai (kisi aur blog se). Isse SIRF topic aur key points samajhne ke liye use karo.
Phir ek BILKUL NAYA, 100% ORIGINAL, usse ZYADA detailed aur behtar blog post likho.
REFERENCE ko HUBAHU COPY mat karo — apne shabdon mein, apne examples aur apne fresh code ke saath likho. (Plagiarism / copyright bilkul nahi.)

Language: explanation clean Devanagari Hindi (हिंदी लिपि) mein + technical terms English mein (React, function, error, API, component, server). Hard/shuddh Hindi mat use karo.
Tone: 50 saal ke experienced senior developer jaisa, dost ko samjhate hue ("दोस्तों", "चलिए शुरू करते हैं").

MUST follow (first-page Google SEO formula):
- HOOK INTRO: relatable problem ya sawaal se shuru karo (boring definition se nahi).
- QUICK ANSWER BOX intro ke turant baad (40-60 words, main keyword ke saath):
  <div style="background:#ecfeff;border-left:4px solid #06b6d4;padding:14px 18px;border-radius:0 10px 10px 0;margin:18px 0;"><strong>⚡ Quick Answer:</strong> [40-60 word seedha jawab]</div>
- <h2> headings ko asli search questions ki tarah likho ("X क्या है?", "X कैसे काम करता है?", "X vs Y में difference?").
- Jahan possible ho ek clean comparison <table> do.
- "Kaise karein" parts ko numbered <ol><li> steps mein.
- Production-ready, complete code <pre><code>...</code></pre> mein (truncate mat karo).
- Common errors / edge cases / best practices discuss karo.
- Ek (sirf ek) external authority link official docs ka do, rel="noopener" target="_blank" ke saath.
- 5 FAQ <details><summary> accordion + neeche JSON-LD FAQPage schema (same 5 Q&A).
- Length: 1500-2500 words, comprehensive, scannable (chhote paragraphs, bold, bullets).

Output format BILKUL aise (aur kuch nahi):
TITLE: [SEO-friendly catchy title, main keyword ke saath, Hinglish]
---
[raw HTML body — koi markdown nahi, koi triple-backtick nahi, seedha HTML]
"""
    prompt = instructions + "\n\n=== REFERENCE ARTICLE (sirf inspiration ke liye — copy mat karo) ===\n" + reference[:8000]

    print("[INFO] Gemini se original better post likhwaa raha hoon... (thoda time lagega)")
    out = ask_gemini(prompt, temperature=0.8)
    if not out:
        print("[ERROR] Gemini se response nahi mila.")
        return

    # TITLE aur body alag karo
    title = ""
    body = out
    if out.upper().startswith("TITLE:"):
        nl = out.find("\n")
        title = out[6:nl].strip() if nl != -1 else ""
        body = out[nl + 1:].lstrip() if nl != -1 else out
        if body.startswith("---"):
            body = body[3:].lstrip()
    # code fences clean
    if body.startswith("```html"):
        body = body[7:]
    elif body.startswith("```"):
        body = body[3:]
    if body.rstrip().endswith("```"):
        body = body.rstrip()[:-3]
    body = body.strip()

    out_file = "rewritten_post.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(body)

    print("\n" + "=" * 44)
    print("✅ ORIGINAL (better) post taiyaar!")
    print("=" * 44)
    if title:
        print(f"\n📌 SUGGESTED TITLE:\n   {title}")
    print(f"\n📄 HTML saved: {out_file}  (~{len(body.split())} words)")
    print("\n👉 Steps:")
    print("   1. Blogger > New Post > upar right '<>' (HTML view) on karo")
    print(f"   2. '{out_file}' kholo, poora content copy karo, HTML view me paste karo")
    print("   3. Title (upar) + labels lagao > Preview > Publish")
    print("\n⚠️  Publish se pehle ek baar padh lena — sab sahi hai na (quality check).")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1].lower()
    if cmd == "topics":
        n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10
        cmd_topics(n)
    elif cmd == "captions":
        if len(sys.argv) < 3:
            print('Usage: python gemini_tools.py captions "Post Title" "post-url"')
            return
        cmd_captions(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif cmd == "faq":
        if len(sys.argv) < 3:
            print('Usage: python gemini_tools.py faq "Post Title"')
            return
        cmd_faq(sys.argv[2])
    elif cmd == "rewrite":
        if len(sys.argv) < 3:
            print('Usage: python gemini_tools.py rewrite "reference.txt"')
            print('(Pehle reference.txt me woh post copy-paste karo jisse inspiration leni hai)')
            return
        cmd_rewrite(sys.argv[2])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
