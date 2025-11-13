import os
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.error import Conflict

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

FB_FEED_URL = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/feed"
FB_PHOTO_URL = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/photos"
FB_VIDEO_URL = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/videos"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    text = message.text or ""
    fb_response = None

    try:
        if message.photo:
            photo_file = await message.photo[-1].get_file()
            photo_url = photo_file.file_path
            fb_response = requests.post(FB_PHOTO_URL, data={
                "url": photo_url,
                "caption": text,
                "access_token": FACEBOOK_PAGE_ACCESS_TOKEN
            })
        elif message.video:
            video_file = await message.video.get_file()
            video_url = video_file.file_path
            fb_response = requests.post(FB_VIDEO_URL, data={
                "file_url": video_url,
                "description": text,
                "access_token": FACEBOOK_PAGE_ACCESS_TOKEN
            })
        elif text:
            fb_response = requests.post(FB_FEED_URL, data={
                "message": text,
                "access_token": FACEBOOK_PAGE_ACCESS_TOKEN
            })

        if fb_response and fb_response.ok:
            post_id = fb_response.json().get("id")
            permalink_request = requests.get(
                f"https://graph.facebook.com/{post_id}",
                params={"fields": "permalink_url", "access_token": FACEBOOK_PAGE_ACCESS_TOKEN}
            )
            if permalink_request.ok:
                permalink = permalink_request.json().get("permalink_url")
                await message.reply_text(f"✅ Posted to Facebook: {permalink}")
            else:
                await message.reply_text("✅ Posted to Facebook, but couldn’t retrieve the link.")
        else:
            await message.reply_text("❌ Failed to post to Facebook.")
            print("Error:", fb_response.text if fb_response else "No response")

    except Exception as e:
        await message.reply_text(f"⚠️ Error: {str(e)}")
        print("Exception:", e)

# Build the bot
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_message))

if __name__ == "__main__":
    print("Bot is running...")
    # run_polling internally handles asyncio, conflicts, and signals
    app.run_polling(stop_signals=None)

