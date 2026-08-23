import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
MY_USERNAME = os.getenv("MY_USERNAME", "YOUR_TELEGRAM_USERNAME")

# مراحل المحادثة
NAME, ID_PHOTOS, PHONE = range(3)

# ------------------ الأوامر والدوال ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك! اختر من القائمة أدناه:",
        reply_markup=main_menu_keyboard()
    )

async def start_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("بدء عملية التسجيل. الرجاء إدخال اسمك الكامل:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("شكراً! الآن قم بإرسال صورة الهوية الوطنية:")
    return ID_PHOTOS

async def get_id_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['id_photo'] = update.message.photo[-1].file_id
    await update.message.reply_text("تم استلام الصورة. الآن يرجى إرسال رقم هاتفك:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "تم إكمال التسجيل بنجاح! شكراً لك.",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "تم إلغاء العملية.",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def withdraw_deposit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "اختر العملية المطلوبة:",
        reply_markup=deposit_withdraw_keyboard()
    )

async def deposit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("يرجى إرسال تفاصيل الإيداع وصورة عن إيصال التحويل:")

async def customer_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("التواصل مع الدعم", url=f"https://t.me/{MY_USERNAME}")]
    ])
    await update.message.reply_text(
        "للتحويل المباشر إلى خدمة العملاء اضغط على الزر أدناه:",
        reply_markup=keyboard
    )

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في القائمة الرئيسية",
        reply_markup=main_menu_keyboard()
    )

async def handle_deposit_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم استلام طلبك وسيتم معالجته في أقرب وقت.")

# ------------------ لوحات الأزرار ------------------

def main_menu_keyboard():
    keyboard = [
        ["القائمة الرئيسية"],
        ["1. إنشاء حساب"],
        ["2. السحب والإيداع", "3. خدمة العملاء"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def deposit_withdraw_keyboard():
    keyboard = [
        [InlineKeyboardButton("سحب", url=f"https://t.me/{MY_USERNAME}")],
        [InlineKeyboardButton("إيداع", callback_data="deposit")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ------------------ التشغيل الرئيسي ------------------

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
    app.add_handler(CallbackQueryHandler(deposit_callback, pattern='^deposit$'))
    app.add_handler(MessageHandler(filters.Regex('السحب والإيداع'), withdraw_deposit_menu))
    app.add_handler(MessageHandler(filters.Regex('خدمة العملاء'), customer_service))
    app.add_handler(MessageHandler(filters.Regex('القائمة الرئيسية'), main_menu_handler))
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_deposit_submission))

    print("البوت يعمل الآن...")
    app.run_polling()
