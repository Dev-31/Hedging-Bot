# bot_test.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is working!")

if __name__ == "__main__":
    token = os.getenv("TELEGRAM_API_KEY")
    if not token:
        print("❌ No API token found.")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    print("🚀 Running bot...")
    app.run_polling()
