import os, sys
from flask import Flask, request
import requests, time

BOT_TOKEN = "8681264819:AAG8MoxzG4IeZ7CV_9L5tlAdxNeWfxZNN3w"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "")
APIFY_ACTOR = "epctex~youtube-video-downloader"
app = Flask(__name__)

def send_message(chat_id, text):
    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True})

def get_download_link(youtube_url):
    if not APIFY_TOKEN:
        return None, "No API token set"
    try:
        r = requests.post(f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/runs",
            headers={"Authorization": f"Bearer {APIFY_TOKEN}", "Content-Type": "application/json"},
            json={"url": youtube_url}, timeout=15)
        if r.status_code != 201:
            return None, f"API error: {r.status_code} - {r.text[:100]}"
        run_id = r.json()["data"]["id"]
        for _ in range(15):
            time.sleep(3)
            s = requests.get(f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/runs/{run_id}",
                headers={"Authorization": f"Bearer {APIFY_TOKEN}"}, timeout=10).json()
            if s.get("data",{}).get("status") == "SUCCEEDED": break
        results = requests.get(f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/runs/{run_id}/dataset/items",
            headers={"Authorization": f"Bearer {APIFY_TOKEN}"}, timeout=10).json()
        if results:
            item = results[0]
            return item.get("downloadUrl") or item.get("url"), item.get("title", "Video")
        return None, "No results"
    except Exception as e:
        return None, str(e)[:100]

@app.route("/", methods=["POST"])
def webhook():
    body = request.get_json()
    if body and "message" in body and "text" in body["message"]:
        msg = body["message"]
        chat_id = msg["chat"]["id"]
        text = msg["text"]
        if text.startswith("/start"):
            send_message(chat_id, f"🎬 YouTube Downloader\n\n📹 Send link\n🎵 /mp3 <link> - Audio\n\nToken set: {bool(APIFY_TOKEN)}")
        elif "youtube.com" in text or "youtu.be" in text:
            send_message(chat_id, f"⏳ Token: {bool(APIFY_TOKEN)}. Downloading...")
            url, title_or_error = get_download_link(text)
            if url:
                send_message(chat_id, f"🎬 {title_or_error}\n\n📥 {url}")
            else:
                send_message(chat_id, f"❌ {title_or_error}")
    return "OK"

if __name__ == "__main__":
    requests.post(f"{API}/setWebhook", json={"url": "https://yt-downloader-bot-ntq9.onrender.com"})
    app.run(host="0.0.0.0", port=10000)