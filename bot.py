import os
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

# ====== CONFIGURATION ======
TOKEN = "7606371201:AAGLVxcMKO945xVRcSHKISXAQDi1K8_d1mQ"  # Your bot token
SHEET_NAME = "DoctrineOfChristResponses"  # Google Sheet name

# ====== GOOGLE SHEETS SETUP ======
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Path to credentials.json mounted as Render Secret File
SERVICE_ACCOUNT_FILE = "/etc/secrets/credentials.json"

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open(SHEET_NAME).sheet1  # First sheet

# ====== BOT STATES ======
NAME, WHATSAPP, Q1, Q2, Q3, Q4, Q5 = range(7)


# ====== HELPER ======
def save_answer(user_id, data):
    """Save answer to Google Sheets"""
    sheet.append_row([user_id, data])


# ====== HANDLERS ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "WELCOME TO DOCTRINE OF CHRIST 🙏\n\nPlease provide your FULL NAME:"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    context.user_data["name"] = update.message.text
    save_answer(user_id, f"Full Name: {update.message.text}")
    await update.message.reply_text("Please provide your WHATSAPP NUMBER:")
    return WHATSAPP


async def get_whatsapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    context.user_data["whatsapp"] = update.message.text
    save_answer(user_id, f"WhatsApp: {update.message.text}")

    keyboard = [[InlineKeyboardButton("✅ YES", callback_data="YES"),
                 InlineKeyboardButton("❌ NO", callback_data="NO")]]
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
    save_answer(user_id, f"Q1: {query.data}")

    if query.data == "NO":
        await query.edit_message_text(
            "🙏 Thank you for your interest.\n"
            "The first question is very important for the teaching journey.\n"
            "Since you’re not ready to commit, we cannot proceed.\n\nGod bless you!"
        )
        return ConversationHandler.END

    # Continue Q2
    keyboard = [[InlineKeyboardButton("✅ YES", callback_data="YES"),
                 InlineKeyboardButton("❌ NO", callback_data="NO")]]
    await query.edit_message_text(
        "2️⃣ Do you have a plan or time set aside each week to go through the sessions thoughtfully?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return Q2


async def handle_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    save_answer(query.from_user.id, f"Q2: {query.data}")

    keyboard = [[InlineKeyboardButton("✅ YES", callback_data="YES"),
                 InlineKeyboardButton("❌ NO", callback_data="NO")]]
    await query.edit_message_text(
        "3️⃣ Are you open to being checked in on occasionally for follow-up and encouragement?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return Q3


async def handle_q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    save_answer(query.from_user.id, f"Q3: {query.data}")

    await query.edit_message_text(
        "4️⃣ What are you personally hoping to gain or grow in through this teaching series?"
    )
    return Q4


async def handle_q4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    save_answer(user_id, f"Q4: {update.message.text}")

    keyboard = [[InlineKeyboardButton("✅ YES", callback_data="YES"),
                 InlineKeyboardButton("❌ NO", callback_data="NO")]]
    await update.message.reply_text(
        "5️⃣ Attendance will be taken during the meeting, and if you are not consistent, "
        "you might be removed from the platform. Is that okay by you?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return Q5


async def handle_q5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    save_answer(query.from_user.id, f"Q5: {query.data}")

    keyboard = [[InlineKeyboardButton("👉 Join Doctrine of Christ Group", url="https://t.me/+gmr8SdD-dbc4MGY8")]]
    await query.edit_message_text(
        "✅ Thank you for answering the questions!\n\n"
        "Please click below to join the Doctrine of Christ Telegram group:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END


# ====== MAIN ======
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
        fallbacks=[]
    )

    app.add_handler(conv_handler)

    print("🤖 Doctrine of Christ bot is running...")
    app.run_polling()  # ✅ Use polling for Render


if __name__ == "__main__":
    main()
