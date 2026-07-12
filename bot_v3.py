import telebot
from telebot import types
import yt_dlp
import os
import time
import logging

# إعداد السجلات
logging.basicConfig(level=logging.INFO)

# --- الإعدادات الأساسية ---
API_TOKEN = '8901365469:AAHKgh1UZEm5PFqbL7Qdtl5AHftVlfg0Ggg'
CHANNEL_USERNAME = '@zzii_xx' 
ADMIN_ID = 0 # سيتم تعيينه تلقائياً عند أول استخدام لـ /admin

bot = telebot.TeleBot(API_TOKEN)
users_db = set()

def add_user(user_id):
    users_db.add(user_id)

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# --- لوحات المفاتيح (Keyboards) ---

def get_subscribe_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_sub = types.InlineKeyboardButton("✅ اشترك في القناة أولاً", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
    btn_done = types.InlineKeyboardButton("🔄 تم الاشتراك", callback_data="check_sub")
    markup.add(btn_sub)
    markup.add(btn_done)
    return markup

def get_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_help = types.InlineKeyboardButton("❗ | كيفية استخدام البوت.", callback_data="help")
    btn_lang = types.InlineKeyboardButton("🇸🇦 | تغيير لغة البوت.", callback_data="lang")
    markup.add(btn_help, btn_lang)
    return markup

# --- معالجة الأوامر ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    add_user(message.from_user.id)
    
    if not check_subscription(message.from_user.id):
        sub_text = (
            "عذراً عزيزي\n\n"
            "عليك الاشتراك بقناة البوت لتحميل الفيديو الخاص بك\n\n"
            f"- https://t.me/{CHANNEL_USERNAME.replace('@', '')}\n\n"
            "‼️ | اشترك ثم ارسل /start"
        )
        bot.send_message(message.chat.id, sub_text, reply_markup=get_subscribe_keyboard())
    else:
        welcome_text = (
            f"👻 | أهلاً بك عزيزي، مع {bot.get_me().first_name} يمكنك تحميل من عدة مواقع متعددة والاستماع اليها في أي وقت،\n\n"
            "📥 | المنصات المدعومة:\n\n"
            "▶️ يوتيوب | 📸 انستكرام\n"
            "🔵 فيسبوك | ❌ تويتر\n"
            "🎵 تيك توك | 👻 سناب شات\n"
            "🧡 ساوند كلاود | 🔴 بينترست\n"
            "💖 لايكي | 🍊 كواي\n"
            "🔹 تيليجرام | 🅱️ PMC Music\n"
            "🔃 تمبلر | 🎬 ديلي موشن\n"
            "🔵 فيميو | 🧵 ثريدز\n"
            "🧩 فانيميت | 🎬 كاب كات\n\n"
            "- قم بإرسال رابط المنشور فقط 🤍\n"
            "ولا تنسى قم بمشاركه البوت لاصدقائك 🤝🏻"
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "check_sub":
        if check_subscription(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ تم التحقق من الاشتراك!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_welcome(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك في القناة بعد!", show_alert=True)
    
    elif call.data == "help":
        help_text = "📖 أرسل رابط الفيديو من أي منصة مدعومة وسيقوم البوت بتحميله لك فوراً!"
        bot.answer_callback_query(call.id, help_text, show_alert=True)
    
    elif call.data == "lang":
        bot.answer_callback_query(call.id, "🌐 اللغة الحالية هي العربية.", show_alert=True)

# --- لوحة التحكم للمدمن ---

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    global ADMIN_ID
    if ADMIN_ID == 0: ADMIN_ID = message.from_user.id
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"👨‍💻 لوحة التحكم\n\n👥 عدد المستخدمين: {len(users_db)}\n\nاستخدم /broadcast للإذاعة.")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.reply_to(message, "📝 أرسل رسالة الإذاعة:")
        bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(message):
    count = 0
    for uid in users_db:
        try:
            bot.send_message(uid, message.text)
            count += 1
        except: pass
    bot.reply_to(message, f"✅ تم الإرسال لـ {count} مستخدم.")

# --- معالجة الروابط والتحميل ---

@bot.message_handler(func=lambda message: message.text and message.text.startswith('http'))
def handle_links(message):
    if not check_subscription(message.from_user.id):
        send_welcome(message)
        return

    msg = bot.reply_to(message, "⏳ جاري التحميل...")
    file_name = f"vid_{message.from_user.id}_{int(time.time())}.mp4"
    
    try:
        ydl_opts = {'outtmpl': file_name, 'format': 'best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message.text])
        
        with open(file_name, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"✅ تم التحميل بواسطة: {CHANNEL_USERNAME}")
        bot.delete_message(message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ !! : عذراً، قمت بإرسال رابط غير صحيح.", message.chat.id, msg.message_id)
    finally:
        if os.path.exists(file_name): os.remove(file_name)

if __name__ == "__main__":
    bot.infinity_polling()
