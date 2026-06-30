"""
fix_broken_images.py — TechIT Broken Image Auto-Fixer
By/for Banti Kevat (TechIT — Tech in Hindi)

Saare LIVE posts scan karta hai. Jin posts ki featured/first image BROKEN (404) ya
MISSING hai, unke liye ImgBB se nayi banner image generate karke post update kar deta hai.

- Purani broken posts (jaise raw.githubusercontent 404 waale) automatically fix.
- ImgBB upload GitHub Actions me hota hai (local sandbox me ImgBB block ho sakta hai),
  isliye ise GitHub Actions (workflow_dispatch) se chalana best hai.

Usage:
  python fix_broken_images.py            (saare posts scan + fix)
  python fix_broken_images.py --scan     (sirf scan/report — koi change nahi)

Reuses auth + banner-gen from auto_post_blogger.py & refresh_old_posts.py.
"""
import os
import sys
import re
import requests

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import auto_post_blogger as a
import refresh_old_posts as r

SCAN_ONLY = "--scan" in sys.argv


def first_image_url(html):
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html or "", re.IGNORECASE)
    return m.group(1) if m else None


def image_ok(url):
    if not url or not url.lower().startswith("http"):
        return False
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.head(url, timeout=15, allow_redirects=True, headers=headers)
        if resp.status_code == 200:
            return True
        # kuch hosts HEAD support nahi karte -> GET try
        resp = requests.get(url, timeout=20, stream=True, headers=headers)
        return resp.status_code == 200
    except Exception:
        return False


def build_banner_html(url, title):
    safe = title.replace('"', "")
    return (
        f'<div class="techit-hero-banner" style="text-align:center;margin-bottom:24px;">'
        f'<img src="{url}" alt="{safe}" '
        f'style="width:100%;max-width:800px;height:auto;border-radius:12px;box-shadow:0 4px 15px rgba(0,0,0,0.15);" />'
        f"</div>\n"
    )


def main():
    service = r.get_blogger_service()
    gemini_key = a.load_gemini_api_key()
    posts = r.list_all_live_posts(service)
    print(f"[INFO] Total LIVE posts: {len(posts)}")
    if SCAN_ONLY:
        print("[MODE] SCAN ONLY — koi post update nahi hoga.\n")

    broken_list, fixed = [], 0
    for post in posts:
        pid = post["id"]
        title = post["title"]
        full = service.posts().get(blogId=a.BLOG_ID, postId=pid).execute()
        html = full.get("content", "") or ""
        labels = full.get("labels", [])
        img = first_image_url(html)

        if img and image_ok(img):
            continue  # image theek hai

        broken_list.append(title)
        status = "MISSING" if not img else "BROKEN(404)"
        print(f"[!] {status}: {title}")

        if SCAN_ONLY:
            continue

        # nayi banner ImgBB se generate karo
        category = (labels[0] if labels else "Coding info")
        try:
            new_url = a.generate_banner(gemini_key, title, category)
        except Exception as e:
            print(f"    [ERROR] banner gen fail: {e}")
            continue
        if not new_url:
            print("    [WARN] banner URL nahi mila — skip")
            continue

        if img and img in html:
            new_html = html.replace(img, new_url)  # broken URL ko nayi se replace
        else:
            new_html = build_banner_html(new_url, title) + html  # image hi nahi thi -> prepend

        try:
            body = {"title": title, "content": new_html}
            if labels:
                body["labels"] = labels
            service.posts().update(blogId=a.BLOG_ID, postId=pid, body=body).execute()
            fixed += 1
            print(f"    [OK] FIXED -> {new_url}")
        except Exception as e:
            print(f"    [ERROR] update fail: {e}")

    print("\n" + "=" * 44)
    print(f"Broken/missing images mile: {len(broken_list)}")
    if not SCAN_ONLY:
        print(f"FIXED: {fixed}")
    if broken_list:
        for t in broken_list:
            print("  -", t)
    print("=" * 44)


if __name__ == "__main__":
    main()
