import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token (replace YOUR_BOT_TOKEN with your actual bot token)
TOKEN = "7606371201:AAGLVxcMKO945xVRcSHKISXAQDi1K8_d1mQ"

# Webhook URL (replace <your-app> with your Render app name)
WEBHOOK_URL = "https://doc-bot-1.onrender.com/webhook"

# Flask app
app = Flask(__name__)
application = None  # telegram application

# Store answers in memory
user_answers = {}

# File to save answers
ANSWERS_FILE = "answers.txt"

# Telegram group link
GROUP_LINK = "https://t.me/+gmr8SdD-dbc4MGY8"


# Save answer to file
def save_answer(user_id, username, answer):
    with open(ANSWERS_FILE, "a", encoding="utf-8") as f:
        f.write(f"UserID: {user_id}, Username: {username}, Answer: {answer}\n")


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "WELCOME TO DOCTRINE OF CHRIST\n\n"
        "1️⃣ The teaching is going to span through 8 weeks.\n"
        "Are you willing to commit to this teaching series with an open and teachable heart? (Yes/No)"
    )


# Handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "NoUsername"

    # First question logic
    if user_id not in user_answers:
        if text in ["yes", "y"]:
            user_answers[user_id] = "yes"
            save_answer(user_id, username, "YES")
            await update.message.reply_text(
                f"✅ Great! Please join our group here: {GROUP_LINK}"
            )
        elif text in ["no", "n"]:
            user_answers[user_id] = "no"
            save_answer(user_id, username, "NO")
            await update.message.reply_text(
                "🙏 Thank you for your interest. "
                "The first question is really needed for the teaching journey."
            )
        else:
            await update.message.reply_text("Please reply with 'Yes' or 'No'.")


# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /start to begin your journey.")


# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200


def main():
    global application
    application = Application.builder().token(TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Handle text replies
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path="webhook",
        webhook_url=WEBHOOK_URL,
    )


if __name__ == "__main__":
    main()
