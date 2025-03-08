import random
import datetime
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Temporary database
users = {}

# Bot Token (Replace with your actual bot token)
TOKEN = "8029651365:AAFBS-wviNLKfbDeBWXXuucTBAEFauyQBig"

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id not in users:
        users[user_id] = {
            "balance": 0, 
            "referrals": 0, 
            "bonus": 0, 
            "last_bonus": None, 
            "last_spin": None, 
            "referral_link": f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
        }
    
    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance")],
        [InlineKeyboardButton("💵 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("🔗 Refer & Earn", callback_data="referral")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="bonus")],
        [InlineKeyboardButton("🎡 Spin & Win", callback_data="spin")],  # Spin button added
        [InlineKeyboardButton("📜 Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        "✨ *Welcome to the Referral Bot!* ✨\n\n"
        "🎯 *Earn ₹5 per referral!*\n"
        "💸 *Withdraw once you reach ₹50!*\n"
        "🎁 *Claim ₹2 daily bonus!*\n"
        "🎡 *Try your luck with Spin & Win!*\n\n"
        f"📌 Your Referral Link: {users[user_id]['referral_link']}\n\n"
        "Use the buttons below to explore!"
    )
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")

# Callback Query Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.message.chat_id
    await query.answer()
    
    if query.data == "balance":
        await query.edit_message_text(
            f"💰 *Your Balance:* ₹{users[user_id]['balance']}\n"
            f"👥 *Total Referrals:* {users[user_id]['referrals']}\n"
            f"🎁 *Daily Bonus Earned:* ₹{users[user_id]['bonus']}",
            parse_mode="Markdown"
        )
    elif query.data == "withdraw":
        if users[user_id]['balance'] >= 50:
            users[user_id]['balance'] -= 50
            await query.edit_message_text("✅ *Withdrawal of ₹50 successful!*", parse_mode="Markdown")
        else:
            await query.edit_message_text("⚠️ *Minimum ₹50 required for withdrawal.*", parse_mode="Markdown")
    elif query.data == "referral":
        await query.edit_message_text(
            f"🔗 *Refer & Earn ₹5 per referral!*\n\n📌 Your Referral Link: {users[user_id]['referral_link']}",
            parse_mode="Markdown"
        )
    elif query.data == "bonus":
        today = datetime.date.today()
        if users[user_id]['last_bonus'] != today:
            users[user_id]['bonus'] += 2  # Daily bonus amount
            users[user_id]['balance'] += 2
            users[user_id]['last_bonus'] = today
            await query.edit_message_text("🎉 *You received ₹2 as a daily bonus!*", parse_mode="Markdown")
        else:
            await query.edit_message_text("⚠️ *You have already claimed your daily bonus today.*", parse_mode="Markdown")
    elif query.data == "spin":
        await spin_task(query, user_id)
    elif query.data == "help":
        await query.edit_message_text(
            "📜 *Help Menu*\n\n"
            "💰 *Check Balance* - View your earnings.\n"
            "💵 *Withdraw* - Withdraw money (Min ₹50).\n"
            "🔗 *Refer & Earn* - Get your referral link.\n"
            "🎁 *Daily Bonus* - Claim ₹2 bonus daily.\n"
            "🎡 *Spin & Win* - Win up to ₹10 daily.\n\n"
            "For any issues, contact support.",
            parse_mode="Markdown"
        )

# Spin Task Function
async def spin_task(query, user_id):
    today = datetime.date.today()
    
    if users[user_id]['last_spin'] == today:
        await query.edit_message_text("⚠️ *You have already used your spin today. Try again tomorrow!*", parse_mode="Markdown")
        return
    
    spin_amount = random.randint(1, 10)  # Random win between ₹1 and ₹10
    users[user_id]['balance'] += spin_amount
    users[user_id]['last_spin'] = today

    await query.edit_message_text(f"🎡 *Spin Result:* You won ₹{spin_amount}! 🎉\n\n💰 *New Balance:* ₹{users[user_id]['balance']}", parse_mode="Markdown")

# Function to delete webhook
async def delete_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
    response = requests.get(url)
    if response.status_code == 200:
        print("Webhook deleted successfully!")
    else:
        print("Error deleting webhook:", response.json())

# Main Function
def main():
    # Delete any existing webhook first
    delete_webhook()
    
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
