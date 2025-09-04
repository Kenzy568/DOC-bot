import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==============================
# 🔹 CONFIGURATION
# ==============================
TOKEN = "YOUR_BOT_TOKEN"  # <-- replace with your bot token
WEBHOOK_URL = "https://your-render-app.onrender.com/webhook"  # <-- replace after deploying to Render

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==============================
# 🔹 TELEGRAM BOT LOGIC
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    await update.message.reply_text(
        "🙏 Welcome to the Doctrine of Christ bot!\n\n"
        "Would you like to join our teaching group on Telegram?"
    )

async def yes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send group link if user says YES"""
    text = update.message.text.strip().lower()
    if text == "yes":
        await update.message.reply_text(
            "✅ Great! Here’s the group link to continue the journey:\n"
            "👉 https://t.me/+gmr8SdD-dbc4MGY8"
        )
    elif text == "no":
        await update.message.reply_text(
            "🙏 Thank you for your interest. The first question is very important for this teaching journey. God bless you."
        )
    else:
        await update.message.reply_text("Please reply with 'YES' or 'NO' 🙏")

# ==============================
# 🔹 FLASK APP (Render uses this)
# ==============================
flask_app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, yes_handler))

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    """Receive updates from Telegram"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK"

# ==============================
# 🔹 STARTUP
# ==============================
if __name__ == "__main__":
    import asyncio

    async def main():
        await application.initialize()
        await application.start()
        # Set webhook
        await application.bot.set_webhook(WEBHOOK_URL)
        print("🤖 Bot is live with webhook!")

    loop = asyncio.get_event_loop()
    loop.create_task(main())
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
