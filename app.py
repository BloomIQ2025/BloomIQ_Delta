from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
import json

app = Flask(__name__)
CORS(app, origins=["*"])

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    with open("credentials.json") as f:
        creds_info = json.load(f)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    client = gspread.authorize(creds)
    sheet = client.open("BloomIQ Gamma").sheet1  # Update this if needed
except Exception as e:
    print(f"Failed to load Google credentials: {e}")
    sheet = None

# Telegram bot setup
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
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
        print(f"Failed to send Telegram message: {e}")

@app.route('/submit', methods=['POST'])
def submit():
    if sheet is None:
        return jsonify({"error": "Google Sheets not initialized"}), 500

    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        city = data.get('city')
        state = data.get('state')

        sheet.append_row([name, email, phone, city, state])

        message = (
            "📢 *New Lead Alert!*\n\n"
            f"*Name:* {name}\n"
            f"*Email:* {email}\n"
            f"*Phone:* {phone}\n"
            f"*City:* {city}\n"
            f"*State:* {state}"
        )
        send_telegram_message(message)

        return jsonify({"message": "Data added to Google Sheet and Telegram notified"}), 200
    except Exception as e:
        print(f"Error in /submit: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
