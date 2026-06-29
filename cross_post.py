"""
TechIT — Cross-Post for Backlinks
=================================
Har naya LIVE post ko Dev.to aur Hashnode par bhi auto-publish karta hai, original
blog ko canonical mark karke. Isse har post se backlink milta hai (SEO boost) +
naya developer audience.

Har platform sirf tab chalta hai jab uska token env me ho — warna skip.

Env:
  Dev.to    : DEVTO_API_KEY
  Hashnode  : HASHNODE_TOKEN, HASHNODE_PUBLICATION_ID
"""
import os
import re
import requests


def _html_to_md(html):
    # JSON-LD <script> aur <style> hata do, phir HTML ko markdown me convert karo.
    html = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", "", html, flags=re.I)
    try:
        from markdownify import markdownify as md
        return md(html, heading_style="ATX", bullets="-")
    except Exception:
        # Fallback: tags strip (markdownify na ho to)
        return re.sub(r"<[^>]+>", "", html)


def _tags(category):
    base = [category, "webdev", "programming", "javascript"]
    seen, out = set(), []
    for t in base:
        slug = re.sub(r"[^a-z0-9]", "", t.lower())[:20]
        if slug and slug not in seen:
            seen.add(slug)
            out.append(slug)
    return out[:4]


def share_to_devto(title, html, canonical_url, category):
    key = os.environ.get("DEVTO_API_KEY", "").strip()
    if not key:
        return None
    article = {"article": {
        "title": title[:128],
        "published": True,
        "body_markdown": _html_to_md(html),
        "canonical_url": canonical_url,
        "tags": _tags(category),
    }}
    try:
        r = requests.post("https://dev.to/api/articles", json=article, timeout=40,
                          headers={"api-key": key, "Content-Type": "application/json"})
        if r.status_code in (200, 201):
            print("[SUCCESS] Dev.to par cross-post ho gaya.")
            return "Dev.to"
        print(f"[WARNING] Dev.to returned {r.status_code}: {r.text[:160]}")
    except Exception as e:
        print(f"[WARNING] Dev.to cross-post failed: {e}")
    return None


def share_to_hashnode(title, html, canonical_url, category):
    token = os.environ.get("HASHNODE_TOKEN", "").strip()
    pub = os.environ.get("HASHNODE_PUBLICATION_ID", "").strip()
    if not token or not pub:
        return None
    query = ("mutation Publish($input: PublishPostInput!){ "
             "publishPost(input: $input){ post{ url } } }")
    variables = {"input": {
        "title": title[:250],
        "publicationId": pub,
        "contentMarkdown": _html_to_md(html),
        "originalArticleURL": canonical_url,
        "tags": [{"slug": t, "name": t} for t in _tags(category)],
    }}
    try:
        r = requests.post("https://gql.hashnode.com/", timeout=40,
                          headers={"Authorization": token, "Content-Type": "application/json"},
                          json={"query": query, "variables": variables})
        data = r.json() if r.status_code == 200 else {}
        if r.status_code == 200 and "errors" not in data:
            print("[SUCCESS] Hashnode par cross-post ho gaya.")
            return "Hashnode"
        print(f"[WARNING] Hashnode: {r.text[:200]}")
    except Exception as e:
        print(f"[WARNING] Hashnode cross-post failed: {e}")
    return None


def cross_post_all(title, html, canonical_url, category):
    """Sab platforms par cross-post. Jahan hua unki list return."""
    if not os.environ.get("DEVTO_API_KEY") and not os.environ.get("HASHNODE_TOKEN"):
        return []  # kuch configured nahi
    print("[INFO] Backlink cross-post shuru (Dev.to / Hashnode)...")
    done = []
    for fn in (share_to_devto, share_to_hashnode):
        r = fn(title, html, canonical_url, category)
        if r:
            done.append(r)
    return done
