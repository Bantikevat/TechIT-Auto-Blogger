import os
import json
import sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("ERROR: Required packages are not installed in the virtual environment.")
    print("Please run: .venv\\Scripts\\pip install google-auth-oauthlib google-api-python-client google-auth-httplib2 requests")
    sys.exit(1)

# Scopes required for Blogger API v3 (Read/Write access to Blogger)
SCOPES = ['https://www.googleapis.com/auth/blogger']

def main():
    print("==================================================")
    print("  TechIT Blogger API OAuth Authorization Setup  ")
    print("==================================================")
    print("Mern Stack auto-posting system ko connect karne ke liye niche diye steps follow karein:")
    print("1. Google Cloud Console (https://console.cloud.google.com) par ek project banayein.")
    print("2. 'Blogger API v3' ko search karke 'Enable' karein.")
    print("3. 'Credentials' tab me jaakar 'Create Credentials' -> 'OAuth client ID' select karein.")
    print("4. Application type me 'Desktop app' select karein, naam dekar create karein.")
    print("5. JSON file download karein aur use rename karke 'client_secrets.json' naam se")
    print("   isi directory (c:\\Claude\\AI_) me save karein.")
    print("==================================================\n")
    
    if not os.path.exists('client_secrets.json'):
        print("[ERROR] 'client_secrets.json' file is directory me nahi mili!")
        print("Please client_secrets.json file ko is folder me copy karein aur script ko phir se run karein.\n")
        return
        
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            scopes=SCOPES
        )
        
        print("[INFO] Browser window open ho rahi hai, please sign-in karein...")
        print("Note: Agar Google unsafe page ki warning de, toh 'Advanced' par click karke 'Go to [Project Name] (unsafe)' select karein.")
        
        # Run local server auth flow
        # prompt='consent' — Google se refresh_token HAMESHA maango (re-auth pe bhi milega).
        # access_type='offline' — refresh token issue karo taaki background me chal sake.
        # Bina in do params ke, dobara authorize karne pe Google refresh_token=None bhej deta hai
        # aur pura auto-poster ruk jata hai.
        creds = flow.run_local_server(
            port=0,
            access_type='offline',
            prompt='consent'
        )
        
        # Extract required credential fields
        credentials_data = {
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'scopes': creds.scopes
        }
        
        # Save credentials to json
        with open('blogger_credentials.json', 'w', encoding='utf-8') as f:
            json.dump(credentials_data, f, indent=4)
            
        print("\n[SUCCESS] Blogger API authorization safal rahi!")
        print("Naya authorization token 'blogger_credentials.json' file me save kar diya gaya hai.")
        print("Ab aap 'auto_post_blogger.py' script ko run kar sakte hain.\n")
        
    except Exception as e:
        print(f"\n[ERROR] Error during setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
