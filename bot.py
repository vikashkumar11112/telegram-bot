from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler
import logging
import requests
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ✅ LOGGING SETUP
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ✅ BOT SETTINGS
CHANNEL_USERNAME = "@referearn01g"
ADMIN_ID = 123456789
users_data = {}
spin_data = {}

# ✅ FUNCTION: Check if user has joined the channel
def is_user_subscribed(user_id, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}"
    response = requests.get(url).json()
    status = response.get("result", {}).get("status", "")
    return status in ["member", "administrator", "creator"]

# ✅ FUNCTION: Start Command
async def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    bot_token = context.bot.token

    if not is_user_subscribed(user_id, bot_token):
        keyboard = [
            [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ Check Subscription", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🚨 Please Join Our Channel", reply_markup=reply_markup)
        return

    referral_link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
    users_data.setdefault(user_id, {"balance": 0, "referrals": 0})
    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance")],
        [InlineKeyboardButton("👥 My Referral Link", callback_data="referral")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus")],
        [InlineKeyboardButton("🎡 Spin & Win", callback_data="spin")],
        [InlineKeyboardButton("🏆 Referral Stats", callback_data="stats")],
        [InlineKeyboardButton("💳 Withdraw", callback_data="withdraw")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"🎉 Welcome {update.message.chat.first_name}!", reply_markup=reply_markup)

# ✅ FUNCTION: Button Handler
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.message.chat_id
    
    if query.data == "balance":
        balance = users_data[user_id]["balance"]
        await query.edit_message_text(f"💰 Your Balance: ₹{balance}")
    
    elif query.data == "referral":
        referral_link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
        await query.edit_message_text(f"🔗 Your Referral Link:\n{referral_link}")
    
    elif query.data == "daily_bonus":
        users_data[user_id]["balance"] += 2
        await query.edit_message_text(f"🎉 You received ₹2 daily bonus!\n💰 New Balance: ₹{users_data[user_id]['balance']}")
    
    elif query.data == "withdraw":
        if users_data[user_id]["balance"] >= 50:
            await context.bot.send_message(ADMIN_ID, f"💰 Withdrawal Request! User: {user_id}, Amount: ₹50")
            users_data[user_id]["balance"] -= 50
            await query.edit_message_text("✅ Withdrawal request sent!")
        else:
            await query.edit_message_text("❌ Minimum ₹50 required for withdrawal!")
    
    elif query.data == "stats":
        referrals = users_data[user_id]["referrals"]
        await query.edit_message_text(f"🏆 You have referred {referrals} people!")
    
    elif query.data == "spin":
        now = datetime.now()
        last_spin = spin_data.get(user_id, None)
        if last_spin and now - last_spin < timedelta(hours=24):
            await query.edit_message_text("❌ You can spin only once every 24 hours!")
        else:
            spin_data[user_id] = now
            reward = random.randint(1, 10)
            users_data[user_id]["balance"] += reward
            await query.edit_message_text(f"🎡 You spun the wheel and won ₹{reward}!\n💰 New Balance: ₹{users_data[user_id]['balance']}")

# ✅ FUNCTION: Handle New Users from Referrals
async def handle_new_user(update: Update, context: CallbackContext):
    args = context.args
    new_user_id = update.message.chat_id

    if args:
        referrer_id = int(args[0])
        if referrer_id != new_user_id and referrer_id in users_data:
            users_data[referrer_id]["balance"] += 5
            users_data[referrer_id]["referrals"] += 1
            await update.message.reply_text("🎉 You joined using a referral link!")
            await context.bot.send_message(referrer_id, f"🎊 New Referral! You earned ₹5.\n💰 New Balance: ₹{users_data[referrer_id]['balance']}")

# ✅ MAIN FUNCTION
def main():
    load_dotenv()
    TOKEN = os.getenv("8029651365:AAERRlXGO9Ekpsrm0wx2P-Bk46ylaVp23Ys")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_user))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
