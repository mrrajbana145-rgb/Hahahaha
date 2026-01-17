import os
import json
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Bot Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8509335052:AAH6ImNyRmhUUBVdQecl7wZqBF8omI2DiHA")
OWNER_ID = 8560626884

# Simple Database
users = {}

def save_users():
    try:
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)
    except:
        pass

try:
    with open("users.json", "r") as f:
        users = json.load(f)
except:
    users = {}

# ========== KEYBOARDS ==========

def main_menu():
    keyboard = [
        [InlineKeyboardButton("📞 Call History", callback_data="history")],
        [InlineKeyboardButton("🔒 History+Recording", callback_data="history_rc")],
        [InlineKeyboardButton("📱 Demo", url="https://t.me/callhistry")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("💳 Add Funds", callback_data="add_funds")],
        [InlineKeyboardButton("🆘 Support", url="http://t.me/Tigertransportbot")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== HANDLERS ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    if user_id not in users:
        users[user_id] = {
            "balance": 9999 if user.id == OWNER_ID else 0,
            "credits": 0,
            "requests": 0,
            "name": user.first_name
        }
        save_users()
    
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n💰 Balance: ₹{users[user_id]['balance']}",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = str(query.from_user.id)
    
    if data == "balance":
        user = users.get(user_id, {"balance": 0, "credits": 0})
        await query.edit_message_text(
            f"💰 Balance: ₹{user['balance']}\n🎯 Credits: {user['credits']}",
            reply_markup=main_menu()
        )
    
    elif data == "add_funds":
        await query.edit_message_text(
            "💳 Enter amount (₹600-₹10000):\nExample: 600 or 1200"
        )
        context.user_data['state'] = 'amount'
    
    elif data == "history":
        keyboard = [
            [InlineKeyboardButton("📞 1 Month - ₹600", callback_data="plan1")],
            [InlineKeyboardButton("📞 2 Months - ₹1200", callback_data="plan2")],
            [InlineKeyboardButton("📞 3 Months - ₹1800", callback_data="plan3")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        await query.edit_message_text(
            "📞 Call History Plans:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "history_rc":
        keyboard = [
            [InlineKeyboardButton("🔒 1 Month + Recording - ₹600", callback_data="plan_rc1")],
            [InlineKeyboardButton("🔒 2 Months + Recording - ₹1200", callback_data="plan_rc2")],
            [InlineKeyboardButton("🔒 3 Months + Recording - ₹1500", callback_data="plan_rc3")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        await query.edit_message_text(
            "🔒 History+Recording Plans:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "back":
        await query.edit_message_text(
            "📍 Main Menu:",
            reply_markup=main_menu()
        )
    
    elif data.startswith("plan"):
        plan_map = {
            "plan1": {"price": 600, "name": "1 Month History"},
            "plan2": {"price": 1200, "name": "2 Months History"},
            "plan3": {"price": 1800, "name": "3 Months History"},
            "plan_rc1": {"price": 600, "name": "1 Month + Recording"},
            "plan_rc2": {"price": 1200, "name": "2 Months + Recording"},
            "plan_rc3": {"price": 1500, "name": "3 Months + Recording"}
        }
        
        if data in plan_map:
            plan = plan_map[data]
            context.user_data['plan'] = plan
            context.user_data['state'] = 'target'
            await query.edit_message_text(
                f"✅ {plan['name']} - ₹{plan['price']}\n\nEnter target number:\n+91XXXXXXXXXX"
            )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = str(update.effective_user.id)
    state = context.user_data.get('state', '')
    
    # Handle amount
    if state == 'amount':
        try:
            amount = int(text)
            if 600 <= amount <= 10000:
                await update.message.reply_photo(
                    photo="https://i.postimg.cc/x1XJXfzb/Screenshot-2025-09-12-22-15-49-26-4336b74596784d9a2aa81f87c2016f50.jpg",
                    caption=f"✅ Deposit ₹{amount}\n\nSend UTR after payment:"
                )
                await update.message.reply_text("📝 Send UTR (12+ characters):")
                context.user_data['state'] = 'utr'
            else:
                await update.message.reply_text("❌ Amount must be ₹600-₹10000")
        except:
            await update.message.reply_text("❌ Invalid amount")
    
    # Handle UTR
    elif state == 'utr':
        if len(text) >= 12:
            await update.message.reply_text(
                f"❌ Payment not received\nUTR: {text[:20]}...\nContact: @Tigertransportbot",
                reply_markup=main_menu()
            )
            context.user_data.clear()
    
    # Handle target number
    elif state == 'target':
        if text.startswith('+91') and len(text) == 13:
            user = users.get(user_id, {"balance": 0, "requests": 0})
            plan = context.user_data.get('plan', {"price": 0, "name": "Plan"})
            
            # Check balance
            if user["balance"] >= plan["price"] or int(user_id) == OWNER_ID:
                if int(user_id) != OWNER_ID:
                    user["balance"] -= plan["price"]
                user["requests"] = user.get("requests", 0) + 1
                users[user_id] = user
                save_users()
                
                # Generate fake history
                report = f"📞 CALL HISTORY REPORT\n\nTarget: {text}\n\n"
                for _ in range(10):
                    num = f"+91{random.choice(['70','80','90','91','92'])}{random.randint(10000000, 99999999)}"
                    date = datetime.now().strftime("%d/%m/%Y")
                    time = f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"
                    report += f"{num} | {date} | {time}\n"
                
                report += f"\n... and 140 more calls"
                
                await update.message.reply_text(report)
                await update.message.reply_text(
                    f"✅ Report generated!\n💰 Balance: ₹{user['balance']}",
                    reply_markup=main_menu()
                )
            else:
                await update.message.reply_text(
                    f"❌ Insufficient balance\nRequired: ₹{plan['price']}",
                    reply_markup=main_menu()
                )
            
            context.user_data.clear()

def main():
    print("🤖 Starting Bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("✅ Bot running!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
