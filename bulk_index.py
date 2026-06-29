"""
TechIT — Bulk Indexer
=====================
Purane saare posts (sitemap se) ko ek baar Google Indexing API + IndexNow par submit karta hai,
taaki jo posts Google me index nahi hue hain woh jaldi crawl ho jayein.

Run:  python bulk_index.py

Zaroori (Google ke liye):  GOOGLE_INDEXING_SA env / google_indexing_sa.json  (service account)
IndexNow (Bing/Yandex) bina kisi key ke chal jata hai.
"""
import re
import time
import requests

# auto_post_blogger se ready-made functions reuse karte hain (DRY)
from auto_post_blogger import submit_to_google_indexing, submit_to_indexnow

SITEMAP_URL = "https://itinfohubs.blogspot.com/sitemap.xml"


def fetch_sitemap_urls():
    print(f"[INFO] Sitemap fetch ho raha hai: {SITEMAP_URL}")
    try:
        r = requests.get(SITEMAP_URL, timeout=30)
        if r.status_code != 200:
            print(f"[ERROR] Sitemap status {r.status_code}")
            return []
        # <loc>...</loc> se saare URLs nikalo
        urls = re.findall(r"<loc>(.*?)</loc>", r.text)
        # sirf actual post pages (search/label etc. nahi)
        posts = [u.strip() for u in urls if "/20" in u]  # blogger post URLs me /YYYY/ hota hai
        print(f"[OK] {len(posts)} post URLs mile.")
        return posts
    except Exception as e:
        print(f"[ERROR] Sitemap fetch failed: {e}")
        return []


def main():
    print("=" * 50)
    print("  TechIT Bulk Indexer (Google + IndexNow)")
    print("=" * 50)

    urls = fetch_sitemap_urls()
    if not urls:
        print("[ERROR] Koi URL nahi mila. Stopping.")
        return

    google_ok = 0
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        # 1. Google Indexing API
        if submit_to_google_indexing(url):
            google_ok += 1
        # 2. IndexNow (Bing/Yandex/DuckDuckGo)
        submit_to_indexnow(url)
        time.sleep(1)  # rate-limit ke liye halka gap

    print("\n" + "=" * 50)
    print(f"[DONE] {len(urls)} URLs process hue. Google submit success: {google_ok}")
    print("Google Search Console me 1-3 din me indexing dikhni chahiye.")
    print("=" * 50)


if __name__ == "__main__":
    main()
