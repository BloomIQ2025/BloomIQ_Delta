from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
import json
import traceback
from datetime import datetime, timezone

app = Flask(__name__)

# ✅ CORS locked to your Vercel domain (and previews, optional)
CORS(app, resources={r"/*": {
    "origins": [
        "https://bloom-iq-delta.vercel.app",     # your live Vercel URL
        r"https://bloom-iq-delta-.*\.vercel\.app"  # optional: allow Vercel previews
    ],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]
}})

# ✅ Google Sheets setup
# Expect GOOGLE_CREDS_JSON to contain the full service account JSON (single-line)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    creds_info = json.loads(os.environ.get("GOOGLE_CREDS_JSON") or "{}")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    client = gspread.authorize(creds)
    # Opens spreadsheet named "BloomIQ Delta" and first tab (Sheet1)
    sheet = client.open("BloomIQ Delta").sheet1
    print("✅ Google Sheets initialized.")
except Exception as e:
    print(f"❌ Failed to load Google credentials or open sheet: {e}")
    traceback.print_exc()
    sheet = None

# ✅ Telegram bot setup (using env vars)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str):
    """Send a Telegram message if credentials exist; otherwise log a warning."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials are missing; skipping Telegram send.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram message sent.")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        traceback.print_exc()

# ✅ Health check
@app.route('/')
def home():
    return "✅ BloomIQ backend is running."

# ✅ Preflight
@app.route('/submit', methods=['OPTIONS'])
def handle_options():
    return '', 204

# ✅ Lead intake
@app.route('/submit', methods=['POST'])
def submit():
    print("🌐 Origin:", request.headers.get("Origin"))

    if sheet is None:
        print("❌ Google Sheet not initialized.")
        return jsonify({"error": "Google Sheets not initialized"}), 500

    try:
        data = request.get_json(force=True, silent=False)
        print("📥 Received data:", data)

        # Existing fields
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        phone = (data.get('phone') or '').strip()
        city = (data.get('city') or '').strip()
        state = (data.get('state') or '').strip()

        # New fields
        raw_privacy = str(data.get('privacy_ack', '')).lower()
        privacy_ack = 'TRUE' if raw_privacy in ('true', '1', 'yes', 'on') else 'FALSE'
        page_url = (data.get('page_url') or '').strip()

        # Server-side timestamp (UTC ISO8601)
        created_at = datetime.now(timezone.utc).isoformat(timespec='seconds')

        # Append in this exact order (A→H):
        # name | email | phone | city | state | privacy_ack | page_url | created_at
        row = [name, email, phone, city, state, privacy_ack, page_url, created_at]
        print("📝 Appending to sheet:", row)
        sheet.append_row(row)  # defaults: USER_ENTERED, inserts at next row

        # Telegram notification (single source of truth)
        message = (
            "📢 *New Lead Alert!*\n\n"
            f"*Name:* {name}\n"
            f"*Email:* {email}\n"
            f"*Phone:* {phone}\n"
            f"*City:* {city}\n"
            f"*State:* {state}\n"
            f"*Privacy Ack:* {privacy_ack}\n"
            f"*Page URL:* {page_url}\n"
            f"*Timestamp (UTC):* {created_at}"
        )
        send_telegram_message(message)

        return jsonify({"message": "Data added to Google Sheet and Telegram notified"}), 200

    except Exception as e:
        print("❌ Error in /submit:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # In Render, gunicorn typically runs this; local debug uses the below
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)