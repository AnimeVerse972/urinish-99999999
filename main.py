import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from anime_data import anime_posts  # Bu alohida faylda turadi

# Render dagi token
API_TOKEN = os.getenv("BOT_TOKEN")

# Sozlamalar
REQUIRED_CHANNEL = "@AniVerseClip"
ADMINS = [6486825926]  # Adminlar ro‘yxati (int ko‘rinishda)

# Logging
logging.basicConfig(level=logging.INFO)

# Bot va dispatcher
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# Obuna tekshiruv funksiyasi
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# /start komandasi
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id

    if not await is_subscribed(user_id):
        keyboard = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("📢 Obuna bo‘lish", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")
        )
        await message.answer("❗ Botdan foydalanish uchun quyidagi kanalga obuna bo‘ling:", reply_markup=keyboard)
        return

    # Foydalanuvchiga menyu tugmalari
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📢 Reklama", "💼 Homiylik")
    await message.answer("✅ Anime kodini yuboring (masalan: 1, 2, 3...)", reply_markup=keyboard)

# Kod yoki tugmalar handleri
@dp.message_handler()
async def handle_input(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    # Tugmalarni qayta ishlash
    if text == "📢 Reklama":
        await message.answer("📩 Reklama uchun @DiyorbekPTMA ga murojaat qiling.")
        return
    elif text == "💼 Homiylik":
        await message.answer("💳 Homiylik uchun karta: 8800904257677885")
        return

    # Obuna tekshirish
    if not await is_subscribed(user_id):
        keyboard = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("📢 Obuna bo‘lish", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")
        )
        await message.answer("❗ Kod yuborishdan oldin kanalga obuna bo‘ling:", reply_markup=keyboard)
        return

    # Kod asosida javob berish
    if text in anime_posts:
        post = anime_posts[text]
        channel_username = post["channel"].strip("@")
        message_id = post["message_id"]

        # Yuklab olish tugmasi (kanaldagi xabarga olib boradi)
        button = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("📥 Yuklab olish / Tomosha qilish", url=f"https://t.me/{channel_username}/{message_id}")
        )

        # Xabarni yuborish
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=post["channel"],
            message_id=message_id,
            reply_markup=button
        )
    else:
        await message.answer("❌ Bunday kod topilmadi. Iltimos, to‘g‘ri kod yuboring.")

# Botni ishga tushirish
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
