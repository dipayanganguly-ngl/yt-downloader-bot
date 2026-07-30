from flask import Flask, request
import requests
import yt_dlp
import os

BOT_TOKEN = "8681264819:AAG8MoxzG4IeZ7CV_9L5tlAdxNeWfxZNN3w"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
app = Flask(__name__)

def send_message(chat_id, text):
    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True})

def extract_url(video_url, quality="best"):
    if quality == "audio": fmt = "bestaudio/best"
    elif quality != "best": fmt = f"best[height<={quality}]"
    else: fmt = "best"
    
    ydl_opts = {
        'format': fmt,
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        # AGGRESSIVE CAMOUFLAGE
        'extractor_args': {
            'youtube': {
                'player_client': ['tv', 'ios', 'mweb', 'android_vr', 'web_safari'],
                'formats': ['missing_pot']
            }
        },
        'headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        'cookiefile': None,
        'geo_bypass': True,
        'geo_bypass_country': 'IN',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return info.get('url'), info.get('title', 'Video')
    except:
        # Fallback to y2mate if yt-dlp fails
        try:
            if "youtu.be" in video_url: vid = video_url.split("/")[-1].split("?")[0]
            elif "watch?v=" in video_url: vid = video_url.split("watch?v=")[1].split("&")[0]
            else: vid = video_url.split("/")[-1]
            k = "mp3" if quality == "audio" else "mp4"
            r = requests.post("https://api.y2mate.is/api/convert", data={"vid": vid, "k": k}, timeout=15)
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
            send_message(chat_id, "🎬 YouTube Downloader\n\n📹 Send link - Best Quality\n🎵 /mp3 <link> - Audio\n🎥 /360 <link> - 360p\n🎥 /720 <link> - 720p")
        elif text.startswith("/mp3") or text.startswith("/360") or text.startswith("/720"):
            parts = text.split(" ", 1)
            cmd = text.split()[0][1:]
            quality_map = {"mp3": "audio", "360": "360", "720": "720"}
            if len(parts) < 2: send_message(chat_id, f"❌ /{cmd} <link>"); return "OK"
            send_message(chat_id, f"⏳ Extracting {cmd}...")
            url, title = extract_url(parts[1], quality_map.get(cmd, "best"))
            send_message(chat_id, f"🎬 {title}\n\n📥 {url}" if url else "❌ Failed. Try /mp3 for audio.")
        elif "youtube.com" in text or "youtu.be" in text:
            send_message(chat_id, "⏳ Extracting best quality...")
            url, title = extract_url(text)
            send_message(chat_id, f"🎬 {title}\n\n📥 {url}\n\n💡 /mp3 | /360 | /720" if url else "❌ Failed. Try /mp3")
    return "OK"

if __name__ == "__main__":
    requests.post(f"{API}/setWebhook", json={"url": "https://yt-downloader-bot-ntq9.onrender.com"})
    app.run(host="0.0.0.0", port=10000)
