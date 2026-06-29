"""
TechIT — Multi-Platform Auto Share
==================================
Naya LIVE post automatically Twitter/X, Facebook Page aur Pinterest par share karta hai.
Har platform sirf tab share karta hai jab uske tokens env me set hon — warna chup-chaap skip
(kuch break nahi hota). Tokens GitHub Secrets me daalein.

Env vars:
  Twitter/X : TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
  Facebook  : FB_PAGE_ID, FB_PAGE_TOKEN
  Pinterest : PINTEREST_TOKEN, PINTEREST_BOARD_ID
"""
import os
import requests


def _env(*names):
    """Saare diye gaye env vars return karo agar sab set hain, warna None."""
    vals = [os.environ.get(n, "").strip() for n in names]
    return vals if all(vals) else None


def share_to_twitter(clean_title, url, category):
    creds = _env("TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET")
    if not creds:
        return None  # configured nahi
    try:
        from requests_oauthlib import OAuth1
        auth = OAuth1(creds[0], creds[1], creds[2], creds[3])
        tag = category.replace(" ", "")
        # Tweet <= 280 chars; URL ~23 ke barabar count hota hai, isliye title trim
        head = clean_title[:180]
        text = f"{head}\n\n{url}\n\n#TechIT #{tag} #coding #Hindi"
        r = requests.post("https://api.twitter.com/2/tweets", json={"text": text}, auth=auth, timeout=20)
        if r.status_code in (200, 201):
            print("[SUCCESS] Twitter/X par share ho gaya.")
            return "Twitter"
        print(f"[WARNING] Twitter returned {r.status_code}: {r.text[:160]}")
    except Exception as e:
        print(f"[WARNING] Twitter share failed: {e}")
    return None


def share_to_facebook(clean_title, url, seo_desc):
    creds = _env("FB_PAGE_ID", "FB_PAGE_TOKEN")
    if not creds:
        return None
    page_id, token = creds
    try:
        msg = f"{clean_title}\n\n{seo_desc}\n\nPadho 👇"
        r = requests.post(f"https://graph.facebook.com/{page_id}/feed",
                          data={"message": msg, "link": url, "access_token": token}, timeout=20)
        if r.status_code == 200:
            print("[SUCCESS] Facebook Page par share ho gaya.")
            return "Facebook"
        print(f"[WARNING] Facebook returned {r.status_code}: {r.text[:160]}")
    except Exception as e:
        print(f"[WARNING] Facebook share failed: {e}")
    return None


def share_to_pinterest(clean_title, url, image_url, seo_desc):
    creds = _env("PINTEREST_TOKEN", "PINTEREST_BOARD_ID")
    if not creds:
        return None
    if not image_url or "http" not in image_url:
        print("[INFO] Pinterest skip — banner image URL nahi mila.")
        return None
    token, board_id = creds
    try:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        body = {
            "board_id": board_id,
            "title": clean_title[:100],
            "description": (seo_desc or clean_title)[:500],
            "link": url,
            "media_source": {"source_type": "image_url", "url": image_url},
        }
        r = requests.post("https://api.pinterest.com/v5/pins", json=body, headers=headers, timeout=25)
        if r.status_code in (200, 201):
            print("[SUCCESS] Pinterest par pin ban gaya.")
            return "Pinterest"
        print(f"[WARNING] Pinterest returned {r.status_code}: {r.text[:160]}")
    except Exception as e:
        print(f"[WARNING] Pinterest share failed: {e}")
    return None


def share_all(clean_title, url, category, seo_desc, image_url):
    """Saare platforms par share karo. Jahan-jahan share hua unki list return karo."""
    print("[INFO] Multi-platform auto-share shuru...")
    shared = []
    for fn, args in (
        (share_to_twitter, (clean_title, url, category)),
        (share_to_facebook, (clean_title, url, seo_desc)),
        (share_to_pinterest, (clean_title, url, image_url, seo_desc)),
    ):
        result = fn(*args)
        if result:
            shared.append(result)
    if shared:
        print(f"[OK] Share hua: {', '.join(shared)}")
    else:
        print("[INFO] Koi social platform configured nahi (tokens missing) — skip.")
    return shared
