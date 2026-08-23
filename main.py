import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot import types

# ----------------- البيانات الأساسية -----------------
# يُفضل ضبط هذه البيانات كـ Environment Variables في موقع Render
TOKEN = os.environ.get("BOT_TOKEN", "ضع_توكن_البوت_هنا")
MY_CHAT_ID = int(os.environ.get("MY_CHAT_ID", "123456789")) # معرف حسابك الرقمي
MY_USERNAME = os.environ.get("MY_USERNAME", "YourTelegramUsername")
# --------------------------------------------------

bot = telebot.TeleBot(TOKEN)

user_data = {}      # لتخزين بيانات كل مستخدم مؤقتاً أثناء إدخالها
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
    bot.send_message(
        message.chat.id, 
        "أهلاً بك! يرجى اختيار الخدمة المطلوبة من القائمة أدناه:", 
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
    phone = message.text
    name = user_data[chat_id]['name']
    photos = user_data[chat_id]['photos']
    username = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"

    # تنسيق رقم العميل بأصفار خانية (مثلاً: 01, 02, 09, 10...)
    client_id_str = f"{client_counter:02d}"

    # إرسال التقرير النهائي إلى حسابك الخاص عبر البوت
    admin_caption = (
        f"📋 **طلب إنشاء حساب جديد**\n\n"
        f"🔢 **العميل رقم:** #{client_id_str}\n"
        f"👤 **الاسم:** {name}\n"
        f"📞 **الرقم:** {phone}\n"
        f"🔗 **اليوزر:** {username}\n"
        f"🆔 **ID تلغرام:** `{chat_id}`"
    )
    
    # إرسال النص إلى حسابك
    bot.send_message(MY_CHAT_ID, admin_caption, parse_mode="Markdown")

    # إرسال صور البطاقة متتالية إلى حسابك
    for i, photo_id in enumerate(photos, 1):
        bot.send_photo(
            MY_CHAT_ID, 
            photo_id, 
            caption=f"📷 **صورة البطاقة ({i}) للعميل رقم #{client_id_str}**"
        )

    # زيادة العداد للعميل القادم
    client_counter += 1

    # تنظيف بيانات المستخدم المؤقتة
    del user_data[chat_id]

    # إعلام المستخدم بالانتهاء
    bot.send_message(
        chat_id, 
        f"تم استلام جميع بياناتك بنجاح! رقم الطلب الخاص بك هو #{client_id_str}. سيتم مراجعة الطلب والتواصل معك قريباً.", 
        reply_markup=main_keyboard()
    )

# ----------------- 2. مسار السحب والإيداع -----------------
@bot.message_handler(func=lambda msg: msg.text == "2. السحب والإيداع")
def withdraw_deposit_menu(message):
    markup = types.InlineKeyboardMarkup()
    btn_withdraw = types.InlineKeyboardButton("سحب", url=f"https://t.me/{MY_USERNAME}?text=اريد%20ان%20أسحب%20أموال")
    btn_deposit = types.InlineKeyboardButton("إيداع", callback_data="deposit")
    markup.add(btn_withdraw, btn_deposit)
    bot.send_message(message.chat.id, "اختر العملية المطلوبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "deposit")
def process_deposit_click(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id, 
        "أرسل عنوانك الخاص (سواءً كان نصاً أو صورة):", 
        reply_markup=cancel_keyboard()
    )
    bot.register_next_step_handler(msg, process_deposit_submission)

def process_deposit_submission(message):
    if message.text == "❌ إلغاء والعودة للقائمة الرئيسية":
        cancel_operation(message)
        return

    chat_id = message.chat.id
    username = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
    
    bot.send_message(chat_id, "تم استلام طلبك وتحويله للقسم المختص.", reply_markup=main_keyboard())

    bot.send_message(
        MY_CHAT_ID, 
        f"💰 **طلب إيداع جديد**\n"
        f"👤 من المستخدم: {username}\n"
        f"🆔 ID: `{chat_id}`",
        parse_mode="Markdown"
    )

    if message.photo:
        bot.send_photo(MY_CHAT_ID, message.photo[-1].file_id, caption="صورة الإيداع المرسلة")
    elif message.text:
        bot.send_message(MY_CHAT_ID, f"📝 التفاصيل / العنوان:\n{message.text}")

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
    print("البوت يعمل الآن...")
    bot.infinity_polling()
