from flask import Flask, request, jsonify
import requests

BOT_TOKEN = "8681264819:AAG8MoxzG4IeZ7CV_9L5tlAdxNeWfxZNN3w"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
app = Flask(__name__)

def send_message(chat_id, text):
    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True})

def get_video(url):
    try:
        if "youtu.be" in url: vid = url.split("/")[-1].split("?")[0]
        elif "watch?v=" in url: vid = url.split("watch?v=")[1].split("&")[0]
        else: vid = url.split("/")[-1]
        r = requests.post("https://api.y2mate.is/api/convert", data={"vid": vid, "k": "mp4"}, timeout=15)
        data = r.json()
        if data.get("dlink"): return data["dlink"], data.get("title", "Video")
    except: pass
    return None, None

@app.route("/", methods=["POST"])
def webhook():
    body = request.get_json()
    if body and "message" in body and "text" in body["message"]:
        msg = body["message"]
        chat_id = msg["chat"]["id"]
        text = msg["text"]
        
        if text.startswith("/start"):
            send_message(chat_id, "🎬 YouTube Downloader\n\n📹 Send link for best quality\n🎵 /mp3 <link> - Audio")
        elif text.startswith("/mp3"):
            parts = text.split(" ", 1)
            if len(parts) < 2: send_message(chat_id, "❌ /mp3 <link>"); return "OK"
            send_message(chat_id, "⏳ Extracting audio...")
            url, title = get_video(parts[1])
            send_message(chat_id, f"🎵 {title}\n\n📥 {url}" if url else "❌ Failed")
        elif "youtube.com" in text or "youtu.be" in text:
            send_message(chat_id, "⏳ Extracting...")
            url, title = get_video(text)
            send_message(chat_id, f"🎬 {title}\n\n📥 {url}\n\n💡 /mp3 for audio" if url else "❌ Failed")
    return "OK"

if __name__ == "__main__":
    requests.post(f"{API}/setWebhook", json={"url": "https://yt-downloader-bot-ntq9.onrender.com"})
    app.run(host="0.0.0.0", port=10000)
