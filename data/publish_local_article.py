import os
import json
import sys

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
except ImportError:
    print("ERROR: Required packages are not installed.")
    print("Please run: .venv\\Scripts\\pip install google-auth-oauthlib google-api-python-client google-auth-httplib2 requests")
    sys.exit(1)

# Configuration
BLOG_ID = "7779383721769805036"
CREDENTIALS_FILE = "blogger_credentials.json"
HTML_FILE = "article_to_post.html"

def main():
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"ERROR: Credentials file '{CREDENTIALS_FILE}' not found. Please run setup_blogger_api.py first.")
        return
        
    if not os.path.exists(HTML_FILE):
        print(f"ERROR: HTML file '{HTML_FILE}' not found.")
        return

    # Load HTML content
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Define post details
    title = "NodeJS Event Loop Tutorial in Hindi - libuv and Thread Pool Explained"
    category = "NodeJS"
    labels = [category, "MERN Stack", "Coding info", "IT EDUCATION"]

    try:
        with open(CREDENTIALS_FILE, "r") as f:
            creds_data = json.load(f)
            
        creds = Credentials(
            token=None,
            refresh_token=creds_data['refresh_token'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            token_uri=creds_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            scopes=creds_data['scopes']
        )
        
        # Refresh access token
        print("[INFO] Refreshing access credentials...")
        creds.refresh(Request())
        
        # Build the Blogger API Client
        service = build('blogger', 'v3', credentials=creds)
        
        post_body = {
            "kind": "blogger#post",
            "blog": {"id": BLOG_ID},
            "title": title,
            "content": html_content,
            "labels": labels
        }
        
        print("[INFO] Uploading post to Blogger in DRAFT mode...")
        posts_service = service.posts()
        request = posts_service.insert(
            blogId=BLOG_ID,
            body=post_body,
            isDraft=True  # Upload as draft first so the user can verify
        )
        response = request.execute()
        
        print("\n[SUCCESS] Post successfully uploaded to Blogger!")
        print(f"Title: {response['title']}")
        print(f"Post ID: {response['id']}")
        print(f"Status: {response['status']}")
        print("Aap apne Blogger Dashboard par jaakar naya post [Draft] check kar sakte hain!\n")
        
    except Exception as e:
        print(f"[ERROR] Blogger API call failed: {e}")

if __name__ == '__main__':
    main()
