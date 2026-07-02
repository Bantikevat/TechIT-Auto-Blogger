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
        # Pagination controls (sirf 6 se zyada posts ho tab dikhega)
        total = len(items)
        pager_html = ""
        if total > 6:
            pager_html = (
                f'<div class="lp-pager" data-total="{total}" data-page="1" data-per="6">'
                f'<button type="button" class="lp-pg-btn lp-pg-prev" disabled>← Previous</button>'
                f'<span class="lp-pg-info">Page <b class="lp-pg-cur">1</b> of <b>{(total + 5) // 6}</b></span>'
                f'<button type="button" class="lp-pg-btn lp-pg-next">Next →</button>'
                f'</div>'
            )
        sections.append(
            f'<section class="lp-sec" id="lp-{cat_id}">'
            f'<div class="lp-sec-h"><span class="lp-e">{emoji}</span>'
            f'<div><b>{name}</b><span>{tagline} · {len(items)} posts</span></div></div>'
            f'<div class="lp-list">{rows}</div>'
            f'{pager_html}'
            f'</section>'
        )

    # Filter chips (click karo → sirf wahi category dikhao)
    nav_links = '<button type="button" class="lp-chip lp-active" data-filter="all">📚 All Topics</button>'
    nav_links += "".join(
        f'<button type="button" class="lp-chip" data-filter="{c[0]}">{c[1]} {c[2]}</button>'
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
.lp-chip{background:#eef2f9;border:1px solid #e4e9f2;color:#1a2233;font-size:13.5px;font-weight:600;padding:8px 14px;border-radius:50px;text-decoration:none;transition:.2s;cursor:pointer;font-family:inherit}
.lp-chip:hover{background:linear-gradient(135deg,#06b6d4,#2563eb);color:#fff;border-color:transparent;transform:translateY(-2px)}
.lp-chip.lp-active{background:linear-gradient(135deg,#0d1b2a,#13263c);color:#fff;border-color:transparent;box-shadow:0 6px 18px rgba(13,27,42,.25)}
.lp-sec.lp-hidden{display:none}
.lp-empty-msg{text-align:center;padding:40px 20px;color:#64748b;font-size:15px}
.lp-empty-msg b{color:#0d1b2a}
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
.lp-item.lp-pg-hidden{display:none}
.lp-pager{display:flex;align-items:center;justify-content:center;gap:14px;margin-top:16px;padding:10px;background:#eef2f9;border-radius:12px;flex-wrap:wrap}
.lp-pg-btn{background:linear-gradient(135deg,#06b6d4,#2563eb);color:#fff;border:0;font-family:inherit;font-weight:700;font-size:13.5px;padding:9px 18px;border-radius:50px;cursor:pointer;transition:.22s;box-shadow:0 4px 12px rgba(6,182,212,.28)}
.lp-pg-btn:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 6px 18px rgba(6,182,212,.4)}
.lp-pg-btn:disabled{background:#cbd5e1;color:#94a3b8;cursor:not-allowed;box-shadow:none}
.lp-pg-info{font-size:13.5px;color:#1a2233;font-weight:500}
.lp-pg-info b{color:#0d1b2a}
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

  <div class="lp-empty-msg" id="lpEmpty" style="display:none">
    Is topic pe abhi koi post nahi hai. <b>Coming soon!</b> 📚<br>
    <small>Instagram <a href="https://www.instagram.com/techit_info/">@techit_info</a> par batao kya banao next!</small>
  </div>

  <div class="lp-foot">
    Naye posts add hote hi yeh page <b>automatically update</b> ho jaata hai.<br>
    Kuch naya seekhna chahte ho? <b>Instagram: <a href="https://www.instagram.com/techit_info/">@techit_info</a></b> par batao — main us par post likh dunga! 🚀
  </div>
</div>
""".strip()

    # Filter JS — separate raw string (f-string ke bahar, taaki JS ke braces safe rahein)
    filter_js = r"""
<script>/*<![CDATA[*/
(function(){
  var chips = document.querySelectorAll('.lp-nav .lp-chip');
  var sections = document.querySelectorAll('.lp-sec');
  var emptyMsg = document.getElementById('lpEmpty');
  if(!chips.length || !sections.length) return;

  // ============== PAGINATION (per section, 6 items per page) ==============
  function renderPage(pager){
    if(!pager) return;
    var section = pager.closest('.lp-sec');
    var items = section.querySelectorAll('.lp-list .lp-item');
    var per = parseInt(pager.getAttribute('data-per'), 10) || 6;
    var page = parseInt(pager.getAttribute('data-page'), 10) || 1;
    var totalPages = Math.max(1, Math.ceil(items.length / per));
    if(page < 1) page = 1;
    if(page > totalPages) page = totalPages;
    pager.setAttribute('data-page', page);
    var start = (page - 1) * per;
    var end = start + per;
    items.forEach(function(item, i){
      if(i >= start && i < end) item.classList.remove('lp-pg-hidden');
      else item.classList.add('lp-pg-hidden');
    });
    var cur = pager.querySelector('.lp-pg-cur');
    if(cur) cur.textContent = page;
    var prev = pager.querySelector('.lp-pg-prev');
    var next = pager.querySelector('.lp-pg-next');
    if(prev) prev.disabled = (page === 1);
    if(next) next.disabled = (page === totalPages);
  }

  // Sabhi pagers initialize karo (default page 1 dikhao — sirf 6 posts)
  document.querySelectorAll('.lp-pager').forEach(function(pager){
    renderPage(pager);
    var prev = pager.querySelector('.lp-pg-prev');
    var next = pager.querySelector('.lp-pg-next');
    if(prev) prev.addEventListener('click', function(){
      var p = parseInt(pager.getAttribute('data-page'), 10) || 1;
      pager.setAttribute('data-page', p - 1);
      renderPage(pager);
      var s = pager.closest('.lp-sec');
      if(s){ var y = s.getBoundingClientRect().top + window.pageYOffset - 80; window.scrollTo({top: y, behavior: 'smooth'}); }
    });
    if(next) next.addEventListener('click', function(){
      var p = parseInt(pager.getAttribute('data-page'), 10) || 1;
      pager.setAttribute('data-page', p + 1);
      renderPage(pager);
      var s = pager.closest('.lp-sec');
      if(s){ var y = s.getBoundingClientRect().top + window.pageYOffset - 80; window.scrollTo({top: y, behavior: 'smooth'}); }
    });
  });

  // ============== FILTER (category chips) ==============
  function applyFilter(filter){
    var shown = 0;
    sections.forEach(function(s){
      var id = s.id.replace('lp-','');
      if(filter === 'all' || id === filter){
        s.classList.remove('lp-hidden');
        shown++;
      } else {
        s.classList.add('lp-hidden');
      }
    });
    // Filter change ho to pager reset karo (page 1 dikhao)
    sections.forEach(function(s){
      var pg = s.querySelector('.lp-pager');
      if(pg){ pg.setAttribute('data-page', 1); renderPage(pg); }
    });
    if(emptyMsg) emptyMsg.style.display = shown === 0 ? 'block' : 'none';
    chips.forEach(function(c){
      c.classList.toggle('lp-active', c.getAttribute('data-filter') === filter);
    });
    if(filter !== 'all'){
      var firstShown = document.querySelector('.lp-sec:not(.lp-hidden)');
      if(firstShown){
        var y = firstShown.getBoundingClientRect().top + window.pageYOffset - 80;
        window.scrollTo({top: y, behavior: 'smooth'});
      }
    }
    try{
      if(filter === 'all') history.replaceState(null,'',window.location.pathname);
      else history.replaceState(null,'','#lp-' + filter);
    }catch(e){}
  }

  chips.forEach(function(c){
    c.addEventListener('click', function(){ applyFilter(c.getAttribute('data-filter')); });
  });

  var hash = (window.location.hash || '').replace('#lp-','');
  if(hash && document.getElementById('lp-'+hash)){
    applyFilter(hash);
  }
})();
/*]]>*/</script>
""".strip()

    return html + "\n" + filter_js


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
