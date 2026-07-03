"""
fix_duplicate_titles.py — TechIT Duplicate "(In Hindi)" Title Fixer

Saare LIVE posts scan karta hai. Jin titles me "(... in Hindi) (In Hindi)" jaisa
duplicate suffix hai unse trailing "(In Hindi)" hata kar post patch kar deta hai.
(Root cause auto_post_blogger.py me fix ho chuka hai — yeh purane posts saaf karta hai.)

Usage:
  python fix_duplicate_titles.py           (scan + fix)
  python fix_duplicate_titles.py --scan    (sirf report, koi change nahi)

Reuses auth from refresh_old_posts.py / auto_post_blogger.py.
"""
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import auto_post_blogger as a
import refresh_old_posts as r

SCAN_ONLY = "--scan" in sys.argv

# "... in Hindi)" ke baad ek aur "(In Hindi)" — trailing wala hatana hai
DUP_RE = re.compile(r"^(.*in hindi\s*\))\s*\(in hindi\)\s*$", re.IGNORECASE)


def main():
    service = r.get_blogger_service()
    posts = r.list_all_live_posts(service)
    print(f"[INFO] {len(posts)} live posts scan ho rahe hain...")

    fixed = 0
    for post in posts:
        title = post.get("title", "")
        m = DUP_RE.match(title)
        if not m:
            continue
        new_title = m.group(1).strip()
        print(f"[FOUND] {title!r}\n    ->  {new_title!r}")
        if SCAN_ONLY:
            continue
        service.posts().patch(
            blogId=a.BLOG_ID, postId=post["id"], body={"title": new_title}
        ).execute()
        fixed += 1
        print("    [OK] Title update ho gaya.")

    if SCAN_ONLY:
        print("[DONE] Scan-only mode — koi change nahi kiya.")
    else:
        print(f"[DONE] {fixed} titles fix hue.")


if __name__ == "__main__":
    main()
