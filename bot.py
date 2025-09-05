import os
import logging
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = "7606371201:AAGLVxcMKO945xVRcSHKISXAQDi1K8_d1mQ"
WEBHOOK_URL = "https://doc-bot-1.onrender.com/webhook"

# Flask app
app = Flask(__name__)
application = None

# File to save answers
ANSWERS_FILE = "answers.txt"

# Conversation states
NAME, WHATSAPP, Q1, Q2, Q3, Q4, Q5 = range(7)

# Telegram group link
GROUP_LINK = "https://t.me/+gmr8SdD-dbc4MGY8"


# Save answer to file
def save_answer(user_id, username, answer):
    with open(ANSWERS_FILE, "a", encoding="utf-8") as f:
        f.write(f"UserID: {user_id}, Username: {username}, Answer: {answer}\n")


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "WELCOME TO DOCTRINE OF CHRIST\n\nPlease provide your full name:"
    )
    return NAME


# Get full name
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("Please provide your WhatsApp number:")
    return WHATSAPP


# Get WhatsApp number
async def get_whatsapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["whatsapp"] = update.message.text.strip()
    await update.message.reply_text(
        "1️⃣ The teaching is going to span through 8 weeks.\n"
        "Are you willing to commit to this teaching series with an open and teachable heart?",
        reply_markup=ReplyKeyboardMarkup([["Yes", "No"]], one_time_keyboard=True),
    )
    return Q1


# Question 1 handler
async def handle_q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "NoUsername"
    name = context.user_data.get("name", "")
    whatsapp = context.user_data.get("whatsapp", "")

    if text in ["yes", "y"]:
        context.user_data["q1"] = "Yes"
        save_answer(user_id, username, f"Name: {name}, WhatsApp: {whatsapp}, Q1: Yes")
        await update.message.reply_text(
            "2️⃣ Do you have a plan or time set aside each week to go through the sessions thoughtfully?",
            reply_markup=ReplyKeyboardMarkup([["Yes", "No"]], one_time_keyboard=True),
        )
        return Q2
    elif text in ["no", "n"]:
        context.user_data["q1"] = "No"
        save_answer(user_id, username, f"Name: {name}, WhatsApp: {whatsapp}, Q1: No")
        await update.message.reply_text(
            "🙏 Thank you for your interest. The first question is really needed for the teaching journey. God bless you! 🙏",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please reply with 'Yes' or 'No'.")
        return Q1


# Question 2 handler
async def handle_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data["q2"] = text
    save_answer(update.message.from_user.id, update.message.from_user.username or "NoUsername", f"Q2: {text}")
    await update.message.reply_text(
        "3️⃣ Are you open to being checked in on occasionally for follow-up and encouragement?",
        reply_markup=ReplyKeyboardMarkup([["Yes", "No"]], one_time_keyboard=True),
    )
    return Q3


# Question 3 handler
async def handle_q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data["q3"] = text
    save_answer(update.message.from_user.id, update.message.from_user.username or "NoUsername", f"Q3: {text}")
    await update.message.reply_text(
        "4️⃣ What are you personally hoping to gain or grow in through this teaching series?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return Q4


# Question 4 handler
async def handle_q4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data["q4"] = text
    save_answer(update.message.from_user.id, update.message.from_user.username or "NoUsername", f"Q4: {text}")
    await update.message.reply_text(
        "5️⃣ Attendance will be taken during meetings. "
        "If you are not consistent, you might be removed from the platform. Is that okay with you?",
        reply_markup=ReplyKeyboardMarkup([["Yes", "No"]], one_time_keyboard=True),
    )
    return Q5


# Question 5 handler
async def handle_q5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data["q5"] = text
    save_answer(update.message.from_user.id, update.message.from_user.username or "NoUsername", f"Q5: {text}")

    await update.message.reply_text(
        f"✅ Thank you for completing the registration! Please join our group here: {GROUP_LINK}",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


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

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            WHATSAPP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_whatsapp)],
            Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_q1)],
            Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_q2)],
            Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_q3)],
            Q4: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_q4)],
            Q5: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_q5)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    # Run webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path="webhook",
        webhook_url=WEBHOOK_URL,
    )


if __name__ == "__main__":
    main()
