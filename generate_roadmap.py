"""
generate_roadmap.py — TechIT Learning Roadmap Auto-Generator
By/for Banti Kevat (TechIT — Tech in Hindi)

Saare live posts fetch karta hai, Gemini se topic + level classify karwaata hai,
aur ek sundar Learning Path HTML page banata hai jo Blogger ke ek page (jaise /p/learn.html)
me paste karna hai. Naye posts add hone par yeh script wapas chalao — page auto-update.

Output: roadmap.html — Blogger page ke HTML view me paste karo.

Usage:
  python generate_roadmap.py

Reuses Blogger auth + Gemini setup from auto_post_blogger.py & refresh_old_posts.py.
"""
import os
import sys
import json
import re
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import auto_post_blogger as a
import refresh_old_posts as r

OUT_FILE = "roadmap.html"

# Categories in the exact learning ORDER we want on the page (top-to-bottom).
# Each: (id, emoji, name, tagline)
CATEGORIES = [
    ("basics",   "🟢", "Foundation (Start Here)",   "Basics — pehle yeh seekho"),
    ("react",    "⚛️",  "React Journey",             "UI banana seekho"),
    ("nextjs",   "🚀", "Next.js",                    "React ka next-level framework"),
    ("nodejs",   "🟩", "Node.js",                    "JavaScript backend"),
    ("express",  "⚡", "Express.js",                 "REST API framework"),
    ("mongodb",  "🍃", "MongoDB / Database",         "Data store karo"),
    ("mern",     "🎯", "MERN Full Stack",            "Full-stack projects"),
    ("errors",   "🐞", "Error Solving",              "Jab problem aaye"),
    ("ai",       "🤖", "AI Tools",                   "Modern AI ka use"),
    ("news",     "📰", "Tech News",                  "Latest updates"),
    ("other",    "📌", "Other",                      "Misc posts"),
]
CAT_IDS = [c[0] for c in CATEGORIES]

LEVEL_ORDER = {"beginner": 1, "intermediate": 2, "advanced": 3}


def classify_post_gemini(gemini_key, title, labels):
    """Return (category_id, level). Falls back to heuristics on failure."""
    prompt = (
        f"Tum TechIT (Tech in Hindi) blog ke content editor ho. Ek post ka title aur labels diye hain. "
        f"Do cheez batao — JSON output me:\n"
        f'1) "category": in me se EXACTLY ek: {CAT_IDS}\n'
        f'2) "level": beginner | intermediate | advanced (kis level ke reader ke liye)\n\n'
        f"Title: {title}\n"
        f"Labels: {labels}\n\n"
        f"Output ONLY raw JSON (no markdown, no explanation): "
        f'{{"category":"...","level":"..."}}'
    )
    out = a.call_gemini(gemini_key, prompt)
    if not out:
        return _fallback_classify(title, labels)
    m = re.search(r'\{.*?\}', out, re.DOTALL)
    if not m:
        return _fallback_classify(title, labels)
    try:
        data = json.loads(m.group(0))
        cat = data.get("category", "").strip().lower()
        lvl = data.get("level", "beginner").strip().lower()
        if cat not in CAT_IDS:
            cat = _fallback_classify(title, labels)[0]
        if lvl not in LEVEL_ORDER:
            lvl = "beginner"
        return cat, lvl
    except Exception:
        return _fallback_classify(title, labels)


def _fallback_classify(title, labels):
    """Simple keyword-based classification if Gemini fails."""
    t = (title + " " + " ".join(labels)).lower()
    if any(k in t for k in ["error", "fix", "solve", "bug", "issue", "not working", "problem"]):
        return "errors", "intermediate"
    if any(k in t for k in ["mern", "full stack", "full-stack"]):
        return "mern", "intermediate"
    if any(k in t for k in ["next.js", "nextjs", "next js", "hydration"]):
        return "nextjs", "intermediate"
    if any(k in t for k in ["mongo", "database", "mongoose"]):
        return "mongodb", "beginner"
    if any(k in t for k in ["express", "req.body", "middleware", "cors", "rest api"]):
        return "express", "intermediate"
    if any(k in t for k in ["node", "npm", "nodejs"]):
        return "nodejs", "beginner"
    if any(k in t for k in ["react", "usestate", "useeffect", "jsx", "hook"]):
        return "react", "beginner"
    if any(k in t for k in ["ai ", "chatgpt", "gemini", "claude", "prompt", "llm", "openai"]):
        return "ai", "beginner"
    if any(k in t for k in ["news", "tv", "gadget", "review"]):
        return "news", "beginner"
    if any(k in t for k in ["kya hai", "basics", "beginner", "javascript basic", "js basic", "html", "css"]):
        return "basics", "beginner"
    return "other", "beginner"


def fetch_all_posts(service):
    posts, token = [], None
    while True:
        res = service.posts().list(
            blogId=a.BLOG_ID, maxResults=100, pageToken=token,
            fetchBodies=False, status="LIVE",
        ).execute()
        posts.extend(res.get("items", []))
        token = res.get("nextPageToken")
        if not token:
            break
    return posts


def _clean_title(t):
    # remove trailing " (in Hindi)", double-Hindi, etc.
    t = re.sub(r"\s*\(?\s*in hindi\s*\)?\s*", " ", t, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", t).strip()


def build_html(grouped, total_posts):
    # grouped: {cat_id: [ {title, url, level, published}, ... sorted ]}
    lvl_pill = {
        "beginner": '<span class="lp-lvl lp-l-b">Beginner</span>',
        "intermediate": '<span class="lp-lvl lp-l-i">Intermediate</span>',
        "advanced": '<span class="lp-lvl lp-l-a">Advanced</span>',
    }
    sections = []
    for cat_id, emoji, name, tagline in CATEGORIES:
        items = grouped.get(cat_id, [])
        if not items:
            continue
        rows = ""
        for idx, p in enumerate(items, 1):
            rows += (
                f'<a class="lp-item lp-l-{p["level"][0]}" href="{p["url"]}">'
                f'<span class="lp-num">{idx:02d}</span>'
                f'<span class="lp-body">'
                f'<span class="lp-t">{p["title"]}</span>'
                f'<span class="lp-m">{lvl_pill[p["level"]]}<span class="lp-d">{p["published"][:10]}</span></span>'
                f'</span>'
                f'<span class="lp-arr">→</span>'
                f'</a>'
            )
        sections.append(
            f'<section class="lp-sec" id="lp-{cat_id}">'
            f'<div class="lp-sec-h"><span class="lp-e">{emoji}</span>'
            f'<div><b>{name}</b><span>{tagline} · {len(items)} posts</span></div></div>'
            f'<div class="lp-list">{rows}</div>'
            f'</section>'
        )

    nav_links = "".join(
        f'<a href="#lp-{c[0]}" class="lp-chip">{c[1]} {c[2]}</a>'
        for c in CATEGORIES
        if grouped.get(c[0])
    )

    css = r"""
<style>
.lp-wrap{max-width:960px;margin:0 auto;padding:8px 0 40px;font-family:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;color:#16213a}
.lp-hero{background:linear-gradient(135deg,#0d1b2a,#13263c);color:#fff;padding:36px 28px;border-radius:20px;position:relative;overflow:hidden;margin-bottom:24px}
.lp-hero::before{content:"";position:absolute;top:-40%;right:-10%;width:60%;height:180%;background:radial-gradient(circle,rgba(6,182,212,.4),transparent 60%);pointer-events:none}
.lp-hero>*{position:relative;z-index:1}
.lp-hero h1{margin:0 0 10px;font:800 30px/1.15 'Sora','Inter',sans-serif;color:#fff}
.lp-hero p{margin:0 0 18px;color:#cbd5e1;font-size:15.5px;line-height:1.7;max-width:640px}
.lp-hero .lp-stats{display:flex;flex-wrap:wrap;gap:22px;margin-top:14px}
.lp-hero .lp-stat b{display:block;font:800 24px/1 'Sora',sans-serif;background:linear-gradient(135deg,#06b6d4,#60a5fa);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.lp-hero .lp-stat span{font-size:12.5px;color:#94a3b8;letter-spacing:.5px;text-transform:uppercase}
.lp-nav{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 28px}
.lp-chip{background:#eef2f9;border:1px solid #e4e9f2;color:#1a2233;font-size:13.5px;font-weight:600;padding:8px 14px;border-radius:50px;text-decoration:none;transition:.2s}
.lp-chip:hover{background:linear-gradient(135deg,#06b6d4,#2563eb);color:#fff;border-color:transparent;transform:translateY(-2px)}
.lp-sec{margin-bottom:34px}
.lp-sec-h{display:flex;align-items:center;gap:14px;margin-bottom:14px}
.lp-sec-h .lp-e{font-size:32px;width:56px;height:56px;border-radius:16px;background:linear-gradient(135deg,#e0f2fe,#dbeafe);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.lp-sec-h b{display:block;font:800 20px/1.2 'Sora',sans-serif;color:#0d1b2a}
.lp-sec-h span{display:block;font-size:13px;color:#64748b;margin-top:3px}
.lp-list{display:flex;flex-direction:column;gap:10px}
.lp-item{display:flex;align-items:center;gap:14px;background:#fff;border:1px solid #e4e9f2;border-radius:14px;padding:14px 16px;text-decoration:none;transition:.22s;position:relative;overflow:hidden}
.lp-item::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:transparent;transition:.22s}
.lp-item.lp-l-b::before{background:#22c55e}
.lp-item.lp-l-i::before{background:#f59e0b}
.lp-item.lp-l-a::before{background:#ef4444}
.lp-item:hover{transform:translateX(4px);box-shadow:0 8px 24px rgba(13,27,42,.08);border-color:#06b6d4}
.lp-num{font:800 20px/1 'Sora',sans-serif;color:#94a3b8;flex-shrink:0;min-width:34px}
.lp-body{flex:1;min-width:0}
.lp-t{display:block;font-weight:700;color:#0d1b2a;font-size:15px;line-height:1.4;margin-bottom:5px}
.lp-m{display:flex;align-items:center;gap:10px}
.lp-lvl{font-size:10.5px;font-weight:700;padding:3px 9px;border-radius:50px;text-transform:uppercase;letter-spacing:.5px}
.lp-l-b{background:#dcfce7;color:#166534}
.lp-l-i{background:#fef3c7;color:#92400e}
.lp-l-a{background:#fee2e2;color:#991b1b}
.lp-d{font-size:12px;color:#94a3b8}
.lp-arr{color:#06b6d4;font-size:22px;font-weight:700;transition:.22s}
.lp-item:hover .lp-arr{transform:translateX(3px)}
.lp-foot{margin-top:34px;padding:22px;background:linear-gradient(135deg,#eef6fb,#eef2fb);border-radius:16px;text-align:center;color:#3b4a64;font-size:14.5px;line-height:1.7}
.lp-foot b{color:#0d1b2a}
@media(max-width:640px){
  .lp-hero{padding:26px 20px}
  .lp-hero h1{font-size:24px}
  .lp-sec-h .lp-e{width:44px;height:44px;font-size:24px;border-radius:12px}
  .lp-sec-h b{font-size:17px}
  .lp-item{padding:12px 14px}
  .lp-t{font-size:14px}
}
</style>
""".strip()

    html = f"""
{css}
<div class="lp-wrap">
  <div class="lp-hero">
    <h1>🚀 TechIT Learning Roadmap</h1>
    <p>Confuse ho kaunsi post pehle padhein? Yeh page aapka <b>step-by-step guide</b> hai. Neeche ke order mein padho — bilkul beginner se lekar advanced tak. Sab kuch <b>Hindi mein</b>, ek jagah organized. 🇮🇳</p>
    <div class="lp-stats">
      <div class="lp-stat"><b>{total_posts}+</b><span>Total posts</span></div>
      <div class="lp-stat"><b>{sum(1 for c in CATEGORIES if grouped.get(c[0]))}</b><span>Learning tracks</span></div>
      <div class="lp-stat"><b>Hindi</b><span>Easy language</span></div>
    </div>
  </div>

  <div class="lp-nav">
    {nav_links}
  </div>

  {''.join(sections)}

  <div class="lp-foot">
    Naye posts add hote hi yeh page <b>automatically update</b> ho jaata hai.<br>
    Kuch naya seekhna chahte ho? <b>Instagram: <a href="https://www.instagram.com/tech_it_info/">@tech_it_info</a></b> par batao — main us par post likh dunga! 🚀
  </div>
</div>
""".strip()
    return html


def main():
    print("=" * 50)
    print("  TechIT Learning Roadmap Generator")
    print("=" * 50)
    gemini_key = a.load_gemini_api_key()
    service = r.get_blogger_service()

    print("[INFO] Live posts fetch ho rahe hain...")
    posts = fetch_all_posts(service)
    print(f"[OK] {len(posts)} posts mile")

    grouped = {cid: [] for cid in CAT_IDS}
    print("[INFO] Gemini se posts classify ho rahe hain (thoda time lagega)...")
    for i, p in enumerate(posts, 1):
        title = _clean_title(p.get("title", ""))
        labels = p.get("labels", []) or []
        cat, lvl = classify_post_gemini(gemini_key, title, labels)
        grouped[cat].append({
            "title": title,
            "url": p.get("url", ""),
            "level": lvl,
            "published": p.get("published", ""),
        })
        print(f"  [{i:2d}/{len(posts)}] {cat:10s} {lvl:12s} | {title[:55]}")
        time.sleep(0.4)  # gentle on Gemini free tier

    # sort each category: beginner -> intermediate -> advanced, then by published date
    for cid in CAT_IDS:
        grouped[cid].sort(key=lambda p: (LEVEL_ORDER.get(p["level"], 9), p["published"]))

    html = build_html(grouped, len(posts))
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print()
    print("=" * 50)
    print(f"[OK] Roadmap HTML ready: {OUT_FILE} ({len(html)} chars)")
    print("=" * 50)

    # LIVE PAGE ke saath auto-sync (agar existing "Roadmap" / "Learning" page mila to update)
    try:
        print("[INFO] Live Blogger page update check ho raha hai...")
        existing = service.pages().list(blogId=a.BLOG_ID).execute().get("items", [])
        target = next(
            (p for p in existing if any(k in p["title"].lower() for k in ["roadmap", "learning path", "start here"])),
            None,
        )
        body = {
            "kind": "blogger#page",
            "title": "🚀 Learning Roadmap — TechIT ka Complete Guide",
            "content": html,
        }
        if target:
            result = service.pages().update(blogId=a.BLOG_ID, pageId=target["id"], body=body).execute()
            print(f"[OK] Live page UPDATED: {result.get('url','(publishing)')}")
        else:
            result = service.pages().insert(blogId=a.BLOG_ID, body=body, isDraft=False).execute()
            print(f"[OK] Live page CREATED: {result.get('url','(publishing)')}")
    except Exception as e:
        print(f"[WARN] Live page sync fail (roadmap.html still ready): {e}")

    if os.environ.get("GITHUB_ACTIONS"):
        try:
            import subprocess
            subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=False)
            subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=False)
            subprocess.run(["git", "add", OUT_FILE], check=False)
            subprocess.run(["git", "commit", "-m", "Update learning roadmap [skip ci]"], check=False)
            subprocess.run(["git", "pull", "--rebase", "--autostash"], check=False)
            subprocess.run(["git", "push"], check=False)
        except Exception as e:
            print(f"[WARN] roadmap.html push fail: {e}")


if __name__ == "__main__":
    main()
