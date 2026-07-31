import os
from flask import Flask, request
import requests, time

BOT_TOKEN = "8681264819:AAG8MoxzG4IeZ7CV_9L5tlAdxNeWfxZNN3w"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
APIFY_ACTOR = "epctex~youtube-video-downloader"
app = Flask(__name__)

def send_message(chat_id, text):
    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True})

def get_download_link(youtube_url):
    r = requests.post(f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/runs",
        headers={"Authorization": f"Bearer {APIFY_TOKEN}", "Content-Type": "application/json"},
        json={"url": youtube_url})
    if r.status_code != 201: return None, None
    run_id = r.json()["data"]["id"]
    for _ in range(30):
        time.sleep(2)
        s = requests.get(f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/runs/{run_id}",
            headers={"Authorization": f"Bearer {APIFY_TOKEN}"}).json()
        if s["data"]["status"] == "SUCCEEDED": break
    else: return None, None
    results = requests.get(f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/runs/{run_id}/dataset/items",
        headers={"Authorization": f"Bearer {APIFY_TOKEN}"}).json()
    if results and len(results) > 0:
        item = results[0]
        url = item.get("downloadUrl") or item.get("url") or item.get("videoUrl")
        return url, item.get("title", "Video")
    return None, None

@app.route("/", methods=["POST"])
def webhook():
    body = request.get_json()
    if body and "message" in body and "text" in body["message"]:
        msg = body["message"]
        chat_id = msg["chat"]["id"]
        text = msg["text"]
        if text.startswith("/start"):
            send_message(chat_id, "🎬 YouTube Downloader\n\n📹 Send link\n🎵 /mp3 <link> - Audio")
        elif text.startswith("/mp3"):
            parts = text.split(" ", 1)
            if len(parts) < 2: send_message(chat_id, "❌ /mp3 <link>"); return "OK"
            send_message(chat_id, "⏳ Extracting audio...")
            url, title = get_download_link(parts[1])
            send_message(chat_id, f"🎵 {title}\n\n📥 {url}" if url else "❌ Failed")
        elif "youtube.com" in text or "youtu.be" in text:
            send_message(chat_id, "⏳ Downloading (may take 30s)...")
            url, title = get_download_link(text)
            send_message(chat_id, f"🎬 {title}\n\n📥 {url}" if url else "❌ Failed")
    return "OK"

if __name__ == "__main__":
    requests.post(f"{API}/setWebhook", json={"url": "https://yt-downloader-bot-ntq9.onrender.com"})
    app.run(host="0.0.0.0", port=10000)