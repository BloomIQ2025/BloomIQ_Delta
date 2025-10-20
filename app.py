from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
import json
import traceback

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
    sheet = client.open("BloomIQ Delta").sheet1
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

        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        city = data.get('city')
        state = data.get('state')

        print("📝 Appending to sheet:", [name, email, phone, city, state])
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
        print("❌ Error in /submit:", e)
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)


Google Sheet tab name and header row:
it's just the default, its called "Sheet1"
Your current form HTML:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Increase Your Warm Leads Today</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    body {
      font-family: 'Inter', sans-serif;
      background-color: #f9f9f9;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
    }

    .form-container {
      background-color: #fff;
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
      padding: 40px;
      width: 100%;
      max-width: 420px;
      box-sizing: border-box;
    }

    h2 {
      text-align: center;
      color: #D4AF37;
      font-weight: 600;
      margin-bottom: 30px;
   ;
      color: #333;
      margin-bottom: 6px;
      display: block;
    }

    input[type="text"],
    input[type="email"],
    input[type="tel"] {
      width: 100%;
      padding: 12px;
      margin: 8px 0 20px;
      border: 1px solid #ccc;
      border-radius: 6px;
      font-size: 14px;
      box-sizing: border-box;
    }

    .checkbox-container {
      margin-bottom: 20px;
      font-size: 13px;
      color: #555;
    }

    .checkbox-container a {
      color: #D4AF37;
      text-decoration: underline;
    }

    button {
      width: 100%;
      padding: 14px;
      background-color: #D4AF37;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: background-color 0.3s ease;
    }

    button:hover {
      background-color: #b8962f;
    }

    .privacy-note {
      font-size: 12px;
      color: #777;
      text-align: center;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <div class="form-container">
    <h2>Increase Your Warm Leads Today</h2>
    <form id="leadForm">
      <label for="name">Full Name</label>
      <input type="text" id="name" name="name" required />

      <label for="email">Email Address</label>
      <input type="email" id="email" name="email" required />

      <label for="phone">Phone Number</label>
      <input type="tel" id="phone" name="phone" required />

      <label for="city">City</label>
      <input type="text" id="city" name="city" required />

      <label for="state">State</label>
      <input type="text" id="state" name="state" required />

      <div class="checkbox-container">
        <input type="checkbox" id="privacyConsent" required />
        <label for="privacyConsent">
          I have read and agree to the 
          https://privacy-policy-taupe-pi.vercel.app
        </label>
      </div>

      <button type="submit">Get Started</button>
    </form>
    <p class="privacy-note">We respect your privacy. Your information is secure with us.</p>
  </div>

  <script src="form.js"></script>
</body>
</html>