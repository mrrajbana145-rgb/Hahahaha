import os
import json
import random
import threading
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Flask App
app = Flask(__name__)

# Bot Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8509335052:AAH6ImNyRmhUUBVdQecl7wZqBF8omI2DiHA")
OWNER_ID = 8560626884

# Database
users_db = {}

def load_db():
    global users_db
    try:
        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                users_db = json.load(f)
    except:
        users_db = {}

def save_db():
    try:
        with open("users.json", "w") as f:
            json.dump(users_db, f, indent=2)
    except:
        pass

load_db()

# ========== KEYBOARD FUNCTIONS ==========

def get_channel_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/+u2-7A1Ecq_tmMWY1")],
        [InlineKeyboardButton("✅ I've Joined", callback_data="joined_channel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📞 Call History", callback_data="call_history")],
        [InlineKeyboardButton("🔒 History + Recording", callback_data="history_rc")],
        [InlineKeyboardButton("📱 Check Demo", url="https://t.me/callhistry")],
        [InlineKeyboardButton("👥 Referral Program", callback_data="referral")],
        [InlineKeyboardButton("💰 Check Balance", callback_data="check_balance")],
        [InlineKeyboardButton("💳 Add Funds", callback_data="add_funds")],
        [InlineKeyboardButton("🆘 Contact Support", url="http://t.me/Tigertransportbot")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_panel():
    keyboard = [
        [InlineKeyboardButton("👥 Total Users", callback_data="admin_total_users")],
        [InlineKeyboardButton("📢 Broadcast to All", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🎯 Target Broadcast", callback_data="admin_target_broadcast")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_history_plans():
    keyboard = [
        [InlineKeyboardButton("📞 1 Month - ₹600", callback_data="plan_history_1")],
        [InlineKeyboardButton("📞 2 Months - ₹1200", callback_data="plan_history_2")],
        [InlineKeyboardButton("📞 3 Months - ₹1800", callback_data="plan_history_3")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_history_rc_plans():
    keyboard = [
        [InlineKeyboardButton("🔒 1 Month + Recording - ₹600", callback_data="plan_rc_1")],
        [InlineKeyboardButton("🔒 2 Months + Recording - ₹1200", callback_data="plan_rc_2")],
        [InlineKeyboardButton("🔒 3 Months + Recording - ₹1500", callback_data="plan_rc_3")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== BOT HANDLERS ==========

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Initialize user if not exists
    if user_id not in users_db:
        users_db[user_id] = {
            "username": user.username or "",
            "balance": 9999 if user.id == OWNER_ID else 0,
            "credits": 0,
            "referrals": [],
            "referral_code": f"REF{user.id}",
            "referred_by": None,
            "history_requests": 0,
            "joined_channel": True if user.id == OWNER_ID else False,
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "last_active": datetime.now().isoformat()
        }
        save_db()
    
    # Check referral code
    if context.args:
        ref_code = context.args[0]
        if ref_code.startswith("REF") and ref_code != users_db[user_id]["referral_code"]:
            try:
                ref_id = int(ref_code[3:])
                if ref_id != user.id:
                    # Add to referrer's credits
                    if str(ref_id) in users_db:
                        users_db[str(ref_id)]["credits"] += 1
                        users_db[str(ref_id)]["referrals"].append(user.id)
                    # Mark user as referred
                    users_db[user_id]["referred_by"] = ref_id
                    save_db()
            except:
                pass
    
    # Owner gets direct access
    if user.id == OWNER_ID:
        await update.message.reply_text(
            f"👑 **WELCOME OWNER**\n\n"
            f"🔐 Administrator Panel Active\n"
            f"💰 Balance: ₹9999\n"
            f"👥 Total Users: {len(users_db)}\n\n"
            f"Select from menu below:",
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
        return
    
    # Check channel for normal users
    if not users_db[user_id]["joined_channel"]:
        await update.message.reply_text(
            "🔒 **CHANNEL VERIFICATION REQUIRED**\n\n"
            "To access premium services, you must join our official channel:\n\n"
            "1. Click 'Join Channel' below\n"
            "2. Join the channel\n"
            "3. Click 'I've Joined'\n\n"
            "This is required for all users.",
            reply_markup=get_channel_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"🌟 **WELCOME {user.first_name}!**\n\n"
            "🔐 **Premium Analysis Services**\n"
            "• Call History Reports\n"
            "• Communication Analysis\n"
            "• Secure Processing\n\n"
            "Select service from menu below:",
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "🆘 **SUPPORT & HELP**\n\n"
        "📞 **Contact Support:** @Tigertransportbot\n\n"
        "💰 **Payment Issues?**\n"
        "1. Ensure minimum deposit is ₹600\n"
        "2. UTR must be 12 characters minimum\n"
        "3. Payments process within 2-12 hours\n\n"
        "🔒 **Service Guarantee:**\n"
        "• 100% Accurate Reports\n"
        "• Secure Processing\n"
        "• Encrypted Delivery\n\n"
        "⚠️ **Important:**\n"
        "• Keep your receipt safe\n"
        "• Do not share reports\n"
        "• Reports valid for 48 hours",
        parse_mode='Markdown'
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text(
            "🔐 **ADMINISTRATOR PANEL**\n\n"
            "Welcome back, Administrator.\n"
            "Select option below:",
            reply_markup=get_admin_panel(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("⛔ Access Denied")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_id_str = str(user_id)
    data = query.data
    
    # Channel join confirmation
    if data == "joined_channel":
        if user_id_str in users_db:
            users_db[user_id_str]["joined_channel"] = True
            save_db()
        
        await query.edit_message_text(
            "✅ **ACCESS GRANTED**\n\n"
            "You can now access all premium services.\n"
            "Select from menu below:",
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
        return
    
    # Main menu
    if data == "main_menu":
        await query.edit_message_text(
            "📍 **MAIN MENU**\nSelect service:",
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
        return
    
    # Check channel verification for normal users
    if user_id != OWNER_ID and (user_id_str not in users_db or not users_db[user_id_str]["joined_channel"]):
        await query.edit_message_text(
            "🔒 **CHANNEL ACCESS REQUIRED**\n\n"
            "Please join our channel first to access services.",
            reply_markup=get_channel_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    # Call History plans
    if data == "call_history":
        await query.edit_message_text(
            "📞 **CALL HISTORY ANALYSIS**\n\n"
            "Select duration for detailed call analysis:\n\n"
            "🔹 **Basic Analysis:** 30 days history\n"
            "🔹 **Extended Analysis:** 60 days history\n"
            "🔹 **Comprehensive Analysis:** 90 days history\n\n"
            "📊 All reports include 150+ unique contacts",
            reply_markup=get_history_plans(),
            parse_mode='Markdown'
        )
        return
    
    # History + Recording plans
    elif data == "history_rc":
        await query.edit_message_text(
            "🔒 **PREMIUM ANALYSIS PACKAGE**\n\n"
            "Advanced service including:\n"
            "• Complete Call History\n"
            "• Communication Analysis\n"
            "• Pattern Recognition\n"
            "• Encrypted Report Delivery\n\n"
            "Select package duration:",
            reply_markup=get_history_rc_plans(),
            parse_mode='Markdown'
        )
        return
    
    # Check Balance
    elif data == "check_balance":
        user = users_db.get(user_id_str, {"balance": 0, "credits": 0, "history_requests": 0})
        await query.edit_message_text(
            f"💰 **ACCOUNT BALANCE**\n\n"
            f"📊 **Account Summary:**\n"
            f"• Available Balance: ₹{user.get('balance', 0)}\n"
            f"• Referral Credits: {user.get('credits', 0)}\n"
            f"• Total Services Used: {user.get('history_requests', 0)}\n\n"
            f"💳 **Deposit Information:**\n"
            f"• Minimum Deposit: ₹600\n"
            f"• Maximum Deposit: ₹10,000\n"
            f"• Instant Processing\n\n"
            f"📈 **Credits System:**\n"
            f"• Current Credits: {user.get('credits', 0)}/100\n"
            f"• Need {100 - user.get('credits', 0)} more for 50% discount\n\n"
            f"Use 'Add Funds' to deposit money.",
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
        return
    
    # Referral Program
    elif data == "referral":
        user = users_db.get(user_id_str, {"referral_code": f"REF{user_id}", "credits": 0, "referrals": []})
        await query.edit_message_text(
            f"👥 **REFERRAL PROGRAM**\n\n"
            f"**Your Referral Code:** `{user.get('referral_code', f'REF{user_id}')}`\n\n"
            f"💎 **Earn Credits:**\n"
            f"• Each successful referral: +1 Credit\n"
            f"• Reach 100 Credits: Get 50% Discount\n\n"
            f"📈 **Your Statistics:**\n"
            f"• Total Credits: {user.get('credits', 0)}\n"
            f"• Successful Referrals: {len(user.get('referrals', []))}\n"
            f"• Referred By: {'REF' + str(user.get('referred_by')) if user.get('referred_by') else 'None'}\n\n"
            f"🔗 **Share this link:**\n"
            f"`https://t.me/Callhistorypaidbot?start={user.get('referral_code', f'REF{user_id}')}`\n\n"
            f"⚠️ Credits are awarded after referred user makes first deposit.",
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
        return
    
    # Add Funds
    elif data == "add_funds":
        context.user_data['state'] = 'waiting_amount'
        await query.edit_message_text(
            "💳 **ADD FUNDS**\n\n"
            "Enter amount to deposit:\n"
            "• Minimum: ₹600\n"
            "• Maximum: ₹10,000\n\n"
            "Example: `600` or `1200`\n\n"
            "⚠️ Only enter numeric amount",
            parse_mode='Markdown'
        )
        return
    
    # Plan selection
    elif data.startswith("plan_"):
        plan_type = data[5:]  # Remove 'plan_' prefix
        plans = {
            "history_1": {"price": 600, "days": 30, "name": "📞 1 Month Call History"},
            "history_2": {"price": 1200, "days": 60, "name": "📞 2 Month Call History"},
            "history_3": {"price": 1800, "days": 90, "name": "📞 3 Month Call History"},
            "rc_1": {"price": 600, "days": 30, "name": "🔒 1 Month History + Recording"},
            "rc_2": {"price": 1200, "days": 60, "name": "🔒 2 Months History + Recording"},
            "rc_3": {"price": 1500, "days": 90, "name": "🔒 3 Months History + Recording"}
        }
        
        if plan_type in plans:
            plan = plans[plan_type]
            user = users_db.get(user_id_str, {"balance": 0})
            
            # Check balance (owner gets free)
            if user.get("balance", 0) < plan["price"] and user_id != OWNER_ID:
                await query.edit_message_text(
                    f"❌ **INSUFFICIENT BALANCE**\n\n"
                    f"Service Cost: ₹{plan['price']}\n"
                    f"Your Balance: ₹{user.get('balance', 0)}\n\n"
                    f"Please add funds to continue.\n"
                    f"Minimum deposit: ₹600",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("💳 Add Funds", callback_data="add_funds"),
                        InlineKeyboardButton("🔙 Back", callback_data="history_rc" if "rc" in plan_type else "call_history")
                    ]]),
                    parse_mode='Markdown'
                )
                return
            
            # Store plan selection
            context.user_data['selected_plan'] = plan_type
            context.user_data['plan_price'] = plan["price"]
            context.user_data['plan_days'] = plan["days"]
            context.user_data['state'] = 'waiting_target_number'
            
            await query.edit_message_text(
                f"✅ **PLAN SELECTED**\n\n"
                f"Service: {plan['name']}\n"
                f"Duration: {plan['days']} days\n"
                f"Price: ₹{plan['price']}\n\n"
                f"📱 **Enter Target Number:**\n"
                f"Format: +91XXXXXXXXXX\n\n"
                f"Example: +919876543210",
                parse_mode='Markdown'
            )
    
    # Admin panel options
    elif user_id == OWNER_ID and data.startswith("admin_"):
        if data == "admin_panel":
            await query.edit_message_text(
                "🔐 **ADMIN PANEL**\n\n"
                "Select option:",
                reply_markup=get_admin_panel(),
                parse_mode='Markdown'
            )
        
        elif data == "admin_total_users":
            # Create user list
            user_list = []
            for uid, user_data in users_db.items():
                user_info = f"ID: {uid} | @{user_data.get('username', 'N/A')} | Balance: ₹{user_data.get('balance', 0)}"
                user_list.append(user_info)
            
            user_text = "\n".join(user_list[:20])  # Show first 20 users
            if len(user_list) > 20:
                user_text += f"\n\n... and {len(user_list)-20} more users"
            
            await query.edit_message_text(
                f"👥 **TOTAL USERS:** {len(users_db)}\n\n"
                f"{user_text}",
                reply_markup=get_admin_panel(),
                parse_mode='Markdown'
            )
        
        elif data == "admin_stats":
            total_balance = sum(u.get("balance", 0) for u in users_db.values())
            total_requests = sum(u.get("history_requests", 0) for u in users_db.values())
            total_credits = sum(u.get("credits", 0) for u in users_db.values())
            
            await query.edit_message_text(
                f"📈 **SYSTEM STATISTICS**\n\n"
                f"👥 **Users:**\n"
                f"• Total Users: {len(users_db)}\n"
                f"• Channel Joined: {sum(1 for u in users_db.values() if u.get('joined_channel', False))}\n\n"
                f"💰 **Financial:**\n"
                f"• Total Balance: ₹{total_balance}\n"
                f"• Average Balance: ₹{total_balance//len(users_db) if users_db else 0}\n"
                f"• Owner Balance: ₹9999\n\n"
                f"📊 **Usage:**\n"
                f"• Total Requests: {total_requests}\n"
                f"• Total Credits: {total_credits}\n"
                f"• Most Active: {max((u.get('history_requests', 0) for u in users_db.values()), default=0)} requests\n\n"
                f"🕐 **Last Updated:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                reply_markup=get_admin_panel(),
                parse_mode='Markdown'
            )
        
        elif data == "admin_broadcast":
            context.user_data['state'] = 'admin_broadcast'
            await query.edit_message_text(
                "📢 **BROADCAST TO ALL USERS**\n\n"
                "Enter your message to send to all users:\n\n"
                "⚠️ This will be sent to all registered users.",
                parse_mode='Markdown'
            )
        
        elif data == "admin_target_broadcast":
            context.user_data['state'] = 'admin_target_broadcast'
            await query.edit_message_text(
                "🎯 **TARGETED BROADCAST**\n\n"
                "Enter user ID followed by message:\n"
                "Format: `user_id message`\n\n"
                "Example: `123456789 Hello, this is a test message`",
                parse_mode='Markdown'
            )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    user_id = update.effective_user.id
    user_id_str = str(user_id)
    text = update.message.text.strip()
    state = context.user_data.get('state', '')
    
    # Handle deposit amount
    if state == 'waiting_amount':
        try:
            amount = int(text)
            
            if amount < 600:
                await update.message.reply_text(
                    "❌ **MINIMUM DEPOSIT ₹600**\n\n"
                    "Please enter amount ₹600 or more.",
                    parse_mode='Markdown'
                )
                return
            
            if amount > 10000:
                await update.message.reply_text(
                    "❌ **MAXIMUM DEPOSIT ₹10,000**\n\n"
                    "Please enter amount ₹10,000 or less.",
                    parse_mode='Markdown'
                )
                return
            
            # Store amount and show payment instructions
            context.user_data['deposit_amount'] = amount
            context.user_data['transaction_id'] = f"TXN{random.randint(100000, 999999)}"
            context.user_data['state'] = 'waiting_utr'
            
            payment_msg = f"""
✅ **DEPOSIT REQUEST CONFIRMED**

📋 **Transaction Details:**
• Amount: ₹{amount}
• Transaction ID: `{context.user_data['transaction_id']}`
• Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📸 **PAYMENT INSTRUCTIONS:**

1. **Scan QR Code Below** or
2. **Send ₹{amount} via UPI**

3. **After payment, send UTR Number**
   (Minimum 12 characters)

⚠️ **Important:**
• Payment must be exact amount
• Send UTR within 1 hour
• Include transaction ID in notes
"""
            
            # Send QR code
            await update.message.reply_photo(
                photo="https://i.postimg.cc/x1XJXfzb/Screenshot-2025-09-12-22-15-49-26-4336b74596784d9a2aa81f87c2016f50.jpg",
                caption=payment_msg,
                parse_mode='Markdown'
            )
            
            # Ask for UTR
            await update.message.reply_text(
                "📝 **ENTER UTR
