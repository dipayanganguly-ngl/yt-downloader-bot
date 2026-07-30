import os
import telebot
import yt_dlp

BOT_TOKEN = "8681264819:AAG8MoxzG4IeZ7CV_9L5tlAdxNeWfxZNN3w"
bot = telebot.TeleBot(BOT_TOKEN)

def extract_url(video_url, quality="best"):
    if quality == "audio": fmt = "bestaudio/best"
    elif quality != "best": fmt = f"best[height<={quality}]"
    else: fmt = "best"
    ydl_opts = {'format': fmt, 'skip_download': True, 'quiet': True, 'extractor_args': {'youtube': {'player_client': ['default', '-android_sdkless']}}}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return info.get('url'), info.get('title', 'Video')
    except: return None, None

@bot.message_handler(commands=['start'])
def start(msg): bot.reply_to(msg, "🎬 Send YouTube link\n🎵 /mp3 <link>\n🎥 /360 <link>\n🎥 /720 <link>")

@bot.message_handler(commands=['mp3'])
def mp3(msg):
    parts = msg.text.split(" ", 1)
    if len(parts) < 2: bot.reply_to(msg, "❌ /mp3 <link>"); return
    bot.reply_to(msg, "⏳ Extracting...")
    url, title = extract_url(parts[1], "audio")
    bot.reply_to(msg, f"🎵 {title}\n\n📥 {url}" if url else "❌ Failed")

@bot.message_handler(commands=['360', '720'])
def quality_cmd(msg):
    q = msg.text.split()[0][1:]
    parts = msg.text.split(" ", 1)
    if len(parts) < 2: bot.reply_to(msg, f"❌ /{q} <link>"); return
    bot.reply_to(msg, f"⏳ Extracting {q}p...")
    url, title = extract_url(parts[1], q)
    bot.reply_to(msg, f"🎬 {title} ({q}p)\n\n📥 {url}" if url else "❌ Failed")

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def handle_link(msg):
    bot.reply_to(msg, "⏳ Extracting...")
    url, title = extract_url(msg.text, "best")
    bot.reply_to(msg, f"🎬 {title}\n\n📥 {url}\n\n💡 /mp3 | /360 | /720" if url else "❌ Failed")

if __name__ == "__main__": bot.infinity_polling()
