"""
refresh_old_posts.py — TechIT Auto-Refresh (SEO freshness)
By/for Banti Kevat (TechIT — Tech in Hindi)

Sabse purane (ya least-recently-refreshed) LIVE post ko Gemini se UPDATE + IMPROVE
karke republish karta hai. Isse Blogger ka 'updated' timestamp + sitemap lastmod
bump hota hai -> Google "fresh content" samajh ke ranking boost deta hai.

- Post ka original banner image preserve hota hai.
- HTML safe-balance hota hai (auto_post_blogger.fix_html_tags se).
- refreshed_posts.json me track hota hai (rotate through saare posts).

Usage:
  python refresh_old_posts.py [N]      (default N=1 post refresh)

Blogger auth + Gemini auto_post_blogger.py se reuse hota hai.
Secrets/files: blogger_credentials.json, gemini_api_key.txt (ya env vars).
"""
import os
import sys
import json
import re
import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import auto_post_blogger as a

REFRESH_LOG = "refreshed_posts.json"
MAX_BODY_CHARS = 12000  # Gemini ko bahut bada HTML mat bhejo


def _now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def get_blogger_service():
    if not os.path.exists(a.CREDENTIALS_FILE):
        print(f"[ERROR] {a.CREDENTIALS_FILE} nahi mili. setup_blogger_api.py chalao ya BLOGGER_CREDENTIALS_JSON secret set karo.")
        sys.exit(1)
    with open(a.CREDENTIALS_FILE, "r", encoding="utf-8") as f:
        creds_data = json.loads(f.read().strip())
    creds = a.Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        token_uri=creds_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        scopes=creds_data["scopes"],
    )
    creds.refresh(a.Request())
    return a.build("blogger", "v3", credentials=creds)


def load_log():
    if os.path.exists(REFRESH_LOG):
        try:
            with open(REFRESH_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_log(log):
    with open(REFRESH_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def list_all_live_posts(service):
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


def pick_post(posts, log):
    # oldest published first; never-refreshed ko priority
    by_pub = sorted(posts, key=lambda p: p.get("published", ""))
    never = [p for p in by_pub if p["id"] not in log]
    if never:
        return never[0]
    # sab kabhi na kabhi refresh ho chuke -> sabse purane refresh wala
    return sorted(by_pub, key=lambda p: log.get(p["id"], ""))[0] if by_pub else None


def _clean_html(html):
    h = html.strip()
    if h.startswith("```html"):
        h = h[7:]
    elif h.startswith("```"):
        h = h[3:]
    if h.rstrip().endswith("```"):
        h = h.rstrip()[:-3]
    return h.strip()


def refresh_one(service, post, gemini_key):
    pid = post["id"]
    title = post["title"]
    full = service.posts().get(blogId=a.BLOG_ID, postId=pid).execute()
    old_html = full.get("content", "") or ""
    labels = full.get("labels", [])

    # original banner ya first image preserve karo (koi image na khoye)
    bm = re.search(r'<div class="techit-hero-banner".*?</div>\s*', old_html, re.DOTALL)
    banner = bm.group(0) if bm else ""
    first_img = ""
    if not banner:
        im = re.search(r'<img[^>]+>', old_html, re.IGNORECASE)
        first_img = im.group(0) if im else ""

    prompt = (
        "Tum TechIT (Tech in Hindi) ke senior editor ho. Neeche ek PURANA blog post (HTML) diya hai. "
        "Ise 2026 ke hisaab se UPDATE aur IMPROVE karo (content REFRESH):\n"
        "- Latest best-practices/info add karo; purani ya galat cheezein fix karo.\n"
        "- SEO upgrade: agar nahi hai to Quick Answer box add karo "
        '(<div style="background:#ecfeff;border-left:4px solid #06b6d4;padding:14px 18px;border-radius:0 10px 10px 0;margin:18px 0;"><strong>⚡ Quick Answer:</strong> ...</div>), '
        "<h2> ko search-question style banao, ek comparison <table>, aur 5 FAQ <details><summary> + JSON-LD FAQPage schema (agar pehle se nahi hai).\n"
        "- Code examples ko modern aur complete <pre><code>...</code></pre> me do.\n"
        "- Language: explanation Devanagari Hindi (हिंदी) + technical terms English. Hard Hindi nahi.\n"
        "- Content original aur behtar ho; thoda lamba/detailed bhi ho sakta hai.\n"
        "- Banner image waala <div class=\"techit-hero-banner\"> mat add karo (woh alag se lag jaayega).\n"
        "Output: SIRF raw HTML body (koi markdown, koi triple-backtick nahi).\n\n"
        f"=== PURANA POST (Title: {title}) ===\n{old_html[:MAX_BODY_CHARS]}"
    )

    new_html = a.call_gemini(gemini_key, prompt)
    if not new_html:
        return False
    new_html = _clean_html(new_html)
    if len(new_html) < 400:
        print("[WARN] Refreshed content bahut chhota — skip (safety).")
        return False

    # banner ya first image wapas prepend (koi image na khoye)
    if banner and "techit-hero-banner" not in new_html:
        new_html = banner + "\n" + new_html
    elif first_img and "<img" not in new_html.lower():
        new_html = '<div style="text-align:center;margin-bottom:20px;">' + first_img + "</div>\n" + new_html

    try:
        new_html = a.fix_html_tags(new_html)
    except Exception:
        pass

    body = {"title": title, "content": new_html}
    if labels:
        body["labels"] = labels
    service.posts().update(blogId=a.BLOG_ID, postId=pid, body=body).execute()
    return True


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1
    gemini_key = a.load_gemini_api_key()
    service = get_blogger_service()

    posts = list_all_live_posts(service)
    print(f"[INFO] Total LIVE posts: {len(posts)}")
    if not posts:
        print("[INFO] Koi live post nahi mila.")
        return

    log = load_log()
    done = 0
    for _ in range(n):
        post = pick_post(posts, log)
        if not post:
            break
        print(f"[INFO] Refreshing: '{post['title']}' (published {post.get('published','')[:10]})")
        try:
            if refresh_one(service, post, gemini_key):
                log[post["id"]] = _now_iso()
                done += 1
                print(f"[OK] Refreshed + republished: {post['title']}")
            else:
                # skip hua to bhi log kar do taaki rotate ho (loop me atke nahi)
                log[post["id"]] = _now_iso()
                print(f"[WARN] Skipped (Gemini issue): {post['title']}")
        except Exception as e:
            print(f"[ERROR] Refresh fail '{post['title']}': {e}")
            log[post["id"]] = _now_iso()
        posts = [p for p in posts if p["id"] != post["id"]]

    save_log(log)
    print(f"[DONE] {done} post(s) refreshed. Log: {REFRESH_LOG}")

    # GitHub Actions me log commit karo
    if os.environ.get("GITHUB_ACTIONS"):
        try:
            import subprocess
            subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=False)
            subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=False)
            subprocess.run(["git", "add", REFRESH_LOG], check=False)
            subprocess.run(["git", "commit", "-m", "Update refresh log [skip ci]"], check=False)
            subprocess.run(["git", "pull", "--rebase"], check=False)
            subprocess.run(["git", "push"], check=False)
        except Exception as e:
            print(f"[WARNING] Log push failed: {e}")


if __name__ == "__main__":
    main()
