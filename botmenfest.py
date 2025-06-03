import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import pytz
import os
from datetime import datetime, timedelta
import asyncio
import random
import pytz

# ======================= CONFIG =======================
BOT_TOKEN = 'Token Bot Mu'
TARGET_CHAT_ID = 'Target CH atau Grup
ADMIN_IDS = [ Id Admin ]
DATA_FILE = 'user_data.json'
STARTING_COINS = 5
COST_PER_MESSAGE = 1
DAILY_LIMIT = 2
RESET_HOUR = 1  # Jam 01:00 WIB reset harian
DELAY_SECONDS = 5  # Delay sebelum mengirim ke channel
AVATAR_FOLDER = 'avatars'  # Folder avatar acak

# ======================= SETUP =======================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def get_random_avatar():
    if not os.path.exists(AVATAR_FOLDER):
        return None
    files = [f for f in os.listdir(AVATAR_FOLDER) if f.endswith(('.jpg', '.png'))]
    if not files:
        return None
    return os.path.join(AVATAR_FOLDER, random.choice(files))

def reset_daily_if_needed(user_data):
    # Reset harian jam 01:00 WIB
    wib = pytz.timezone('Asia/Jakarta')
    now = datetime.now(wib)
    last_reset_str = user_data.get("last_reset")
    if last_reset_str:
        last_reset = datetime.fromisoformat(last_reset_str)
        last_reset = wib.localize(last_reset.replace(tzinfo=None))
    else:
        last_reset = now - timedelta(days=1)
    # Reset jika sudah lewat jam 01:00 WIB hari ini
    reset_time = now.replace(hour=RESET_HOUR, minute=0, second=0, microsecond=0)
    if now >= reset_time and (last_reset < reset_time):
        user_data["daily"] = DAILY_LIMIT
        user_data["last_reset"] = now.isoformat()

# ======================= COMMANDS =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = {"coins": STARTING_COINS, "daily": DAILY_LIMIT, "last_reset": None, "sent": 0}
        save_data(data)
    await update.message.reply_text(
        "Halo! Kirim pesanmu ke aku, dan akan aku teruskan ke channel secara anonim. 1 pesan = 1 koin. "
        "Gunakan hashtag #ask dan sertakan username kamu seperti @contoh di awal pesan. "
        "Ketik /saldo untuk cek sisa koinmu."
    )

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    user_data = data.get(user_id, {"coins": 0, "daily": 0, "last_reset": None, "sent": 0})
    reset_daily_if_needed(user_data)
    coins = user_data.get("coins", 0)
    daily = user_data.get("daily", DAILY_LIMIT)
    await update.message.reply_text(f"Sisa koin kamu: {coins}\nSisa daily chat hari ini: {daily}")

async def topup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return await update.message.reply_text("Kamu bukan admin!")

    if len(context.args) != 2:
        return await update.message.reply_text("Format: /topup <id_user> <jumlah>")

    target_id, jumlah = context.args
    data = load_data()
    if target_id not in data:
        data[target_id] = {"coins": STARTING_COINS, "daily": DAILY_LIMIT, "last_reset": None, "sent": 0}
    data[target_id]["coins"] += int(jumlah)
    save_data(data)
    await update.message.reply_text(f"Berhasil menambahkan {jumlah} koin ke {target_id}.")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Silakan laporkan ID pengguna dan alasan kamu ke admin langsung. Fitur report otomatis akan segera hadir.")

async def statistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return await update.message.reply_text("Kamu bukan admin!")

    data = load_data()
    total_users = len(data)
    total_sent = sum(d.get("sent", 0) for d in data.values())
    await update.message.reply_text(f"📊 Statistik:\nTotal pengguna: {total_users}\nTotal pesan dikirim: {total_sent}")

# ======================= MESSAGE HANDLER =======================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    wib = pytz.timezone('Asia/Jakarta')
    now = datetime.now(wib)

    user_data = data.setdefault(user_id, {"coins": STARTING_COINS, "daily": DAILY_LIMIT, "last_reset": None, "sent": 0})
    reset_daily_if_needed(user_data)

    if user_data["daily"] <= 0:
        return await update.message.reply_text("Kamu sudah mengirim maksimal 2 pesan hari ini. Tunggu hingga besok 01:00 WIB untuk mengirim lagi.")

    if user_data["coins"] < COST_PER_MESSAGE:
        return await update.message.reply_text("Koin kamu tidak cukup. Hubungi admin untuk topup.")

    message = update.message.text.strip()
    if not message.lower().startswith("#ask"):
        return await update.message.reply_text("Pesan harus diawali dengan hashtag #ask.")

    if not any(word.startswith("@") for word in message.split()):
        return await update.message.reply_text("Kamu harus mencantumkan username diawali dengan @.")

    user_data["coins"] -= COST_PER_MESSAGE
    user_data["daily"] -= 1
    user_data["sent"] += 1
    user_data["last_reset"] = now.isoformat()
    save_data(data)

    await update.message.reply_text("Pesanmu akan dikirim secara anonim dalam beberapa detik...")
    await asyncio.sleep(DELAY_SECONDS)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Laporkan", callback_data=f"report_{user_id}")]
    ])

    avatar = get_random_avatar()
    if avatar:
        with open(avatar, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=TARGET_CHAT_ID,
                photo=photo,
                caption=f"📩 Pesan anonim:\n\n{message}",
                reply_markup=keyboard
            )
    else:
        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=f"📩 Pesan anonim:\n\n{message}",
            reply_markup=keyboard
        )

    await update.message.reply_text("Pesanmu berhasil dikirim secara anonim.")

# ======================= MAIN =======================
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("saldo", saldo))
    application.add_handler(CommandHandler("topup", topup))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("statistik", statistik))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
