"""
TechIT — Garbage Post Cleanup
=============================
Galti se publish hue "prompt-jaise" posts (jaise "Act as a Senior Software Architect...")
ko dhoondh kar DRAFT me revert karta hai (delete nahi — recoverable rehta hai).

Run:  python cleanup_garbage_post.py
"""
import os
import json
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

BLOG_ID = "7779383721769805036"
CREDENTIALS_FILE = "blogger_credentials.json"

# In patterns wale titles "garbage" maane jayenge (lowercase match)
GARBAGE_PATTERNS = [
    "act as a", "faang mentor", "you are an expert", "ignore previous",
    "system prompt", "as an ai language model",
]


def get_service():
    if not os.path.exists(CREDENTIALS_FILE) or os.path.getsize(CREDENTIALS_FILE) == 0:
        print(f"[ERROR] {CREDENTIALS_FILE} missing/empty.")
        sys.exit(1)
    with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
        creds_data = json.load(f)
    creds = Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        token_uri=creds_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        scopes=creds_data["scopes"],
    )
    creds.refresh(Request())
    return build("blogger", "v3", credentials=creds)


def main():
    print("=" * 50)
    print("  TechIT Garbage Post Cleanup")
    print("=" * 50)
    service = get_service()

    posts = service.posts().list(blogId=BLOG_ID, maxResults=100, status="LIVE").execute()
    items = posts.get("items", [])
    print(f"[INFO] {len(items)} live posts mile. Garbage check ho raha hai...")

    found = 0
    for p in items:
        title_l = p["title"].lower()
        if any(pat in title_l for pat in GARBAGE_PATTERNS):
            found += 1
            print(f"\n[GARBAGE] '{p['title']}'")
            print(f"          URL: {p.get('url', 'n/a')}")
            try:
                service.posts().revert(blogId=BLOG_ID, postId=p["id"]).execute()
                print("          -> DRAFT me revert ho gaya (public se hat gaya, recoverable).")
            except Exception as e:
                print(f"          -> Revert failed: {e}")

    if found == 0:
        print("\n[OK] Koi garbage post nahi mila. Sab clean hai!")
    else:
        print(f"\n[DONE] {found} garbage post(s) draft me revert hue.")


if __name__ == "__main__":
    main()
