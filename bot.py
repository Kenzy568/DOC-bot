import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)
import gspread
from google.oauth2.service_account import Credentials
from flask import Flask, request

# -----------------------------
# CONFIG
# -----------------------------

TOKEN = "7606371201:AAGLVxcMKO945xVRcSHKISXAQDi1K8_d1mQ"  # <-- your bot token

# States
NAME, WHATSAPP, Q1, Q2, Q3, Q4, Q5 = range(7)

# Google Sheets Setup
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS_FILE = "credentials.json"  # Place your JSON key in your Render repo
SHEET_NAME = "DoctrineBotResponses"  # Your Google Sheet name

credentials = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPE)
gc = gspread.authorize(credentials)
sheet = gc.open(SHEET_NAME).sheet1  # Use first sheet

# -----------------------------
# FUNCTIONS
# -----------------------------

def save_answer_to_sheet(user_id, data):
    """Append response to Google Sheet"""
    row = [user_id] + data  # user_id + list of answers
    sheet.append_row(row)

# -----------------------------
# TELEGRAM HANDLERS
# -----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("WELCOME TO DOCTRINE OF CHRIST 🙏\n\nPlease provide your FULL NAME:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Please provide your WHATSAPP NUMBER:")
    return WHATSAPP

async def get_whatsapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["whatsapp"] = update.message.text
    # Start Q1
    keyboard = [
        [InlineKeyboardButton("✅ YES", callback_data="YES"),
         InlineKeyboardButton("❌ NO", callback_data="NO")]
    ]
    await update.message.reply_text(
        "1️⃣ The teaching is going to span through a minimum of 8 weeks.\n"
        "Are you willing to commit to this teaching series with an open and teachable heart?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return Q1

async def handle_q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["Q1"] = query.data

    if query.data == "NO":
        await query.edit_message_text(
            "🙏 Thank you for your interest.\n"
            "The first question is very important for the teaching journey.\n"
            "Since you’re not ready to commit, we cannot proceed.\n\nGod bless you!"
        )
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("✅ YES", callback_data="YES"),
         InlineKeyboardButton("❌ NO", callback_data="NO")]
    ]
    await query.edit_message_text(
        "2️⃣ Do you have a plan or time set aside each week to go through the sessions thoughtfully?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return Q2

async def handle_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["Q2"] = query.data

    keyboard = [
        [InlineKeyboardButton("✅ YES", callback_data="YES"),
         InlineKeyboardButton("❌ NO", callback_data="NO")]
    ]
    await query.edit_message_text(
        "3️⃣ Are you open to being checked in on occasionally for follow-up and encouragement?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return Q3

async def handle_q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["Q3"] = query.data

    await query.edit_message_text(
        "4️⃣ What are you personally hoping to gain or grow in through this teaching series?"
    )
    return Q4

async def handle_q4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Q4"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("✅ YES", callback_data="YES"),
         InlineKeyboardButton("❌ NO", callback_data="NO")]
    ]
    await update.message.reply_text(
        "5️⃣ Attendance will be taken during the meeting, and if you are not consistent, "
        "you might be removed from the platform. Is that okay by you?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return Q5

async def handle_q5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["Q5"] = query.data

    # Save all answers to Google Sheet
    data = [
        context.user_data.get("name"),
        context.user_data.get("whatsapp"),
        context.user_data.get("Q1"),
        context.user_data.get("Q2"),
        context.user_data.get("Q3"),
        context.user_data.get("Q4"),
        context.user_data.get("Q5")
    ]
    save_answer_to_sheet(query.from_user.id, data)

    keyboard = [
        [InlineKeyboardButton("👉 Join Doctrine of Christ Group", url="https://t.me/+gmr8SdD-dbc4MGY8")]
    ]
    await query.edit_message_text(
        "✅ Thank you for answering the questions!\n\n"
        "Please click below to join the Doctrine of Christ Telegram group:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

# -----------------------------
# MAIN APP
# -----------------------------

app_flask = Flask(__name__)

@app_flask.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put(update)
    return "ok"

@app_flask.route("/")
def index():
    return "Bot is running!"

bot_app = Application.builder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        WHATSAPP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_whatsapp)],
        Q1: [CallbackQueryHandler(handle_q1)],
        Q2: [CallbackQueryHandler(handle_q2)],
        Q3: [CallbackQueryHandler(handle_q3)],
        Q4: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_q4)],
        Q5: [CallbackQueryHandler(handle_q5)],
    },
    fallbacks=[]
)

bot_app.add_handler(conv_handler)

# Set webhook for Render
WEBHOOK_URL = f"https://YOUR_RENDER_URL/{TOKEN}"  # replace YOUR_RENDER_URL with your Render service URL
bot_app.bot.set_webhook(WEBHOOK_URL)

# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🤖 Doctrine of Christ bot is running on Render.com...")
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
