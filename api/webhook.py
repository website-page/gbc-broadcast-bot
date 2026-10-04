import os
import json
from http.server import BaseHTTPRequestHandler
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# In-memory storage for demo tracking (chats collect as users message or add the bot)
KNOWN_CHATS = set()
STORED_BROADCASTS = {
    "morning": "☀️ Morning Trading Broadcast: Check out today's key setups!",
    "night": "🌙 Night Trading Broadcast: Reviewing today's market performance."
}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data.decode('utf-8'))
            
            # Extract message details safely
            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"].get("text", "")
                KNOWN_CHATS.add(chat_id)
                
                # Command handling
                if text.startswith("/setmorning"):
                    new_text = text.replace("/setmorning", "").strip()
                    if new_text:
                        STORED_BROADCASTS["morning"] = new_text
                        self.send_telegram_message(chat_id, f"✅ Morning broadcast updated successfully!")
                    else:
                        self.send_telegram_message(chat_id, "⚠️ Usage: /setmorning <your message>")
                        
                elif text.startswith("/setnight"):
                    new_text = text.replace("/setnight", "").strip()
                    if new_text:
                        STORED_BROADCASTS["night"] = new_text
                        self.send_telegram_message(chat_id, f"✅ Night broadcast updated successfully!")
                    else:
                        self.send_telegram_message(chat_id, "⚠️ Usage: /setnight <your message>")
                        
                elif text.startswith("/start"):
                    welcome_msg = (
                        "🤖 Bot is active and running on Vercel!\n\n"
                        "Commands:\n"
                        "/setmorning <text> - Set morning broadcast\n"
                        "/setnight <text> - Set night broadcast"
                    )
                    self.send_telegram_message(chat_id, welcome_msg)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def send_telegram_message(self, chat_id, text):
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text})
