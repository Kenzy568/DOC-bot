import os
import json
import gspread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

# =========================
# ⚠️ Your bot token here
# =========================
TOKEN = "7606371201:AAGLVxcMKO945xVRcSHKISXAQDi1K8_d1mQ"  # Replace with your actual bot token

# =========================
# Webhook setup for Render
# =========================
PORT = int(os.environ.get("PORT", 8443))
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")  # Render auto sets this
WEBHOOK_URL = f"{RENDER_URL}/{TOKEN}"  # Telegram webhook

# =========================
# Google Sheets setup
# =========================
SHEET_NAME = "DoctrineResponses"

# Load service account credentials
SERVICE_ACCOUNT_PATH = "/etc/secrets/credentials.json"
gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
sheet = gc.open(SHEET_NAME).sheet1

# =========================
# Conversation states
# =========================
NAME, WHATSAPP, Q1, Q2, Q3, Q4, Q5 = range(7)


# =========================
# Helper to save to Google Sheets
# =========================
def save_answer(user_id, question, answer):
    sheet.append_row([str(user_id), question, answer])


# =========================
# Start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "WELCOME TO DOCTRINE OF CHRIST 🙏\n\nPlease provide your FULL NAME:"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    context.user_data["name"] = update.message.text
    save_answer(user_id, "Full Name", update.message.text)
    await update.message.reply_text("Please provide your WHATSAPP NUMBER:")
    return WHATSAPP


async def get_whatsapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    context.user_data["whatsapp"] = update.message.text
    save_answer(user_id, "WhatsApp", update.message.text)

    # Q1
    keyboard = [
        [InlineKeyboardButton("✅ YES", callback_data="YES"),
         InlineKeyboardButton("❌ NO", callback_data="NO")]
    ]
    await update.message.reply_text(
        "1️⃣ The teaching is going to span a minimum of 8 weeks.\n"
        "Are you willing to commit to this teaching series with an open and teachable heart?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return Q1


async def handle_q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    save_answer(user_id, "Q1", query.data)

    if query.data == "NO":
        await query.edit_message_text(
            "🙏 Thank you for your interest.\n"
            "The first question is very important for the teaching journey.\n"
            "Since you’re not ready to commit, we cannot proceed.\n\nGod bless you!"
        )
        return ConversationHandler.END

    # Continue to Q2
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
    user_id = query.from_user.id
    save_answer(user_id, "Q2", query.data)

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
    user_id = query.from_user.id
    save_answer(user_id, "Q3", query.data)

    await query.edit_message_text(
        "4️⃣ What are you personally hoping to gain or grow in through this teaching series?"
    )
    return Q4


async def handle_q4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    save_answer(user_id, "Q4", update.message.text)

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
    user_id = query.from_user.id
    save_answer(user_id, "Q5", query.data)

    keyboard = [
        [InlineKeyboardButton("👉 Join Doctrine of Christ Group", url="https://t.me/+gmr8SdD-dbc4MGY8")]
    ]
    await query.edit_message_text(
        "✅ Thank you for answering the questions!\n\n"
        "Please click below to join the Doctrine of Christ Telegram group:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END


# =========================
# Main function
# =========================
def main():
    app = Application.builder().token(TOKEN).build()

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
        fallbacks=[],
    )

    app.add_handler(conv_handler)

    print("🤖 Doctrine of Christ bot is running on Render...")

    # Webhook for Render
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL,
    )


if __name__ == "__main__":
    main()
