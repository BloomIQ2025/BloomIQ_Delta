from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
import json
import traceback
from datetime import datetime, timezone  # NEW

app = Flask(__name__)

# ✅ Allow requests from your Vercel frontend
CORS(app, resources={r"/*": {
    "origins": "https://bloom-iq-delta.vercel.app",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]
}})

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    creds_info = json.loads(os.environ.get("GOOGLE_CREDS_JSON"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    client = gspread.authorize(creds)
    sheet = client.open("BloomIQ Delta").sheet1  # "Sheet1"
except Exception as e:
    print(f"❌ Failed to load Google credentials: {e}")
    traceback.print_exc()
    sheet = None

# Telegram bot setup
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials are missing.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        traceback.print_exc()

# ✅ Health check route
@app.route('/')
def home():
    return "✅ BloomIQ backend is running."

# ✅ Handle preflight CORS requests
@app.route('/submit', methods=['OPTIONS'])
def handle_options():
    return '', 204

@app.route('/submit', methods=['POST'])
def submit():
    if sheet is None:
        print("❌ Google Sheet not initialized.")
        return jsonify({"error": "Google Sheets not initialized"}), 500

    try:
        data = request.get_json()
        print("📥 Received data:", data)

        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        phone = (data.get('phone') or '').strip()
        city = (data.get('city') or '').strip()
        state = (data.get('state') or '').strip()

        # NEW fields from client
        raw_privacy = str(data.get('privacy_ack', '')).lower()
        privacy_ack = 'TRUE' if raw_privacy in ('true', '1', 'yes', 'on') else 'FALSE'
        page_url = (data.get('page_url') or '').strip()

        # NEW: server-side timestamp (UTC, ISO8601)
        created_at = datetime.now(timezone.utc).isoformat(timespec='seconds')

        row = [name, email, phone, city, state, privacy_ack, page_url, created_at]
        print("📝 Appending to sheet:", row)
        sheet.append_row(row)

        # Keep Telegram alert, now with timestamp added for your visibility
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
        return jsonify({"error": "Internal server error"}), 500
if __name__ == '__main__':
    app.run(debug=True)