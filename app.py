from flask import Flask, request
import telebot
import requests
import os

BOT_TOKEN = "8681264819:AAG8MoxzG4IeZ7CV_9L5tlAdxNeWfxZNN3w"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def get_video_info(url):
    try:
        if "youtu.be" in url: vid = url.split("/")[-1].split("?")[0]
        elif "watch?v=" in url: vid = url.split("watch?v=")[1].split("&")[0]
        else: vid = url.split("/")[-1]
        r = requests.post("https://api.y2mate.is/api/convert", data={"vid": vid, "k": "mp4"})
        data = r.json()
        if data.get("dlink"): return data["dlink"], data.get("title", "Video")
    except: pass
    return None, None

@bot.message_handler(commands=['start'])
def start(msg): bot.reply_to(msg, "🎬 Send YouTube link\n🎵 /mp3 <link>")

@bot.message_handler(commands=['mp3'])
def mp3(msg):
    parts = msg.text.split(" ", 1)
    if len(parts) < 2: bot.reply_to(msg, "❌ /mp3 <link>"); return
    url, title = get_video_info(parts[1])
    bot.reply_to(msg, f"🎵 {title}\n\n📥 {url}" if url else "❌ Failed")

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def handle_link(msg):
    bot.reply_to(msg, "⏳ Extracting...")
    url, title = get_video_info(msg.text)
    bot.reply_to(msg, f"🎬 {title}\n\n📥 {url}" if url else "❌ Failed")

@app.route("/", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_json())])
    return "OK"

@app.route("/")
def home(): return "YT Bot Running"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url="https://yt-downloader-bot-ntq9.onrender.com")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
