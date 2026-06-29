"""
TechIT — Weekly SEO Report
==========================
Har hafte Google Search Console se data nikaalta hai (clicks, impressions, top
keywords, top pages) aur ek report banakar Telegram par bhejta hai + repo me
markdown file save karta hai.

Service account (GOOGLE_INDEXING_SA / google_indexing_sa.json) use karta hai —
woh Search Console ka Owner hona chahiye (already hai). Cloud project me
"Google Search Console API" enable hona chahiye.

Run:  python weekly_report.py
"""
import os
import io
import json
import sys
import datetime

import requests

# Windows console (cp1252) par emoji print crash na ho — UTF-8 force karo
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request as GRequest
except ImportError:
    print("ERROR: google-auth missing. pip install google-auth")
    sys.exit(1)

SITE_URL = "https://itinfohubs.blogspot.com/"
SC_API = "https://www.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query"
REPORTS_DIR = "reports"


def get_credentials():
    sa_info = None
    env_sa = os.environ.get("GOOGLE_INDEXING_SA", "").strip()
    if env_sa:
        sa_info = json.loads(env_sa)
    elif os.path.exists("google_indexing_sa.json"):
        with open("google_indexing_sa.json", "r", encoding="utf-8") as f:
            sa_info = json.load(f)
    if not sa_info:
        print("[ERROR] Service account JSON nahi mila (GOOGLE_INDEXING_SA).")
        sys.exit(1)
    return service_account.Credentials.from_service_account_info(
        sa_info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])


def query_sc(token, start, end, dimensions, row_limit=10):
    url = SC_API.format(site=requests.utils.quote(SITE_URL, safe=""))
    body = {"startDate": start, "endDate": end, "dimensions": dimensions, "rowLimit": row_limit}
    r = requests.post(url, headers={"Authorization": f"Bearer {token}",
                                    "Content-Type": "application/json"}, json=body, timeout=30)
    if r.status_code == 200:
        return r.json().get("rows", [])
    print(f"[WARNING] SC query {dimensions} returned {r.status_code}: {r.text[:200]}")
    return []


def notify_telegram(text):
    tok = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    cid = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not tok or not cid:
        print("[INFO] Telegram configured nahi — report sirf file me save hogi.")
        return
    try:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", timeout=15,
                          data={"chat_id": cid, "text": text, "parse_mode": "HTML",
                                "disable_web_page_preview": "true"})
        print("[OK] Telegram report sent." if r.status_code == 200 else f"[WARN] TG {r.status_code}: {r.text[:120]}")
    except Exception as e:
        print(f"[WARNING] Telegram failed: {e}")


def main(today_iso):
    print("=" * 50)
    print("  TechIT Weekly SEO Report")
    print("=" * 50)

    creds = get_credentials()
    creds.refresh(GRequest())
    token = creds.token

    end = datetime.date.fromisoformat(today_iso)
    start = end - datetime.timedelta(days=7)
    s, e = start.isoformat(), end.isoformat()

    totals = query_sc(token, s, e, [], row_limit=1)
    clicks = round(totals[0]["clicks"]) if totals else 0
    impressions = round(totals[0]["impressions"]) if totals else 0
    ctr = round(totals[0]["ctr"] * 100, 1) if totals else 0
    pos = round(totals[0]["position"], 1) if totals else 0

    queries = query_sc(token, s, e, ["query"], 10)
    pages = query_sc(token, s, e, ["page"], 5)

    # Build report text
    lines = [
        f"📊 <b>TechIT Weekly SEO Report</b>",
        f"<i>{s} → {e}</i>\n",
        f"👁 Impressions: <b>{impressions}</b>",
        f"🖱 Clicks: <b>{clicks}</b>",
        f"📈 CTR: <b>{ctr}%</b>  |  Avg position: <b>{pos}</b>\n",
        f"🔝 <b>Top Search Queries:</b>",
    ]
    if queries:
        for i, q in enumerate(queries[:7], 1):
            lines.append(f"{i}. {q['keys'][0]} — {round(q['clicks'])} clicks, {round(q['impressions'])} impr")
    else:
        lines.append("   (Abhi koi search data nahi — naya blog, index hone do)")
    lines.append("\n📄 <b>Top Pages:</b>")
    if pages:
        for p in pages[:5]:
            lines.append(f"• {p['keys'][0].replace(SITE_URL, '/')} — {round(p['clicks'])} clicks")
    else:
        lines.append("   (Data aane do — 1-2 hafte)")

    report = "\n".join(lines)
    print("\n" + report.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))

    # Save markdown file
    os.makedirs(REPORTS_DIR, exist_ok=True)
    md_path = os.path.join(REPORTS_DIR, f"seo-report-{e}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report.replace("<b>", "**").replace("</b>", "**").replace("<i>", "_").replace("</i>", "_"))
    print(f"\n[OK] Report saved: {md_path}")

    notify_telegram(report)
    print("[DONE] Weekly report complete.")


if __name__ == "__main__":
    # Date arg se aata hai (workflow se), warna error — kyunki sandbox me Date.now nahi
    arg = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("REPORT_DATE", "")
    if not arg:
        print("[ERROR] Date chahiye: python weekly_report.py YYYY-MM-DD")
        sys.exit(1)
    main(arg)
