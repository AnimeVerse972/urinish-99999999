import logging
import asyncio
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

from anime_data import anime_posts

# TOKEN va kanal ID
BOT_TOKEN = os.getenv("BOT_TOKEN")
REQUIRED_CHANNEL = "@AniVerseClip"
ADMIN_IDS = [6486825926]  # admin user ID(lar)i

# Botni ishga tushirish
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Majburiy obuna tekshirish funksiyasi
async def is_subscribed(user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return chat_member.status in ["member", "creator", "administrator"]
    except Exception:
        return False

# Obuna bo‘lish tugmasi
def subscription_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga obuna bo‘lish", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")],
        [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")]
    ])

# Bosh menyu tugmasi (adminlar uchun ham)
def main_keyboard(user_id: int):
    buttons = [
        [InlineKeyboardButton(text="🎬 Kod yuborish", callback_data="send_code")]
    ]
    if user_id in ADMIN_IDS:
        buttons.append([InlineKeyboardButton(text="⚙️ Admin panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Start komandasi
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if not await is_subscribed(user_id):
        await message.answer("👋 Botdan foydalanish uchun quyidagi kanalga obuna bo‘ling:", reply_markup=subscription_keyboard())
    else:
        await message.answer("🎬 Anime kodini yuboring:", reply_markup=main_keyboard(user_id))

# Callback handler: obuna tekshirish
@dp.callback_query(F.data == "check_subscription")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_subscribed(user_id):
        await callback.message.edit_text("✅ Siz muvaffaqiyatli obuna bo‘lgansiz!\nEndi anime kodini yuboring.", reply_markup=main_keyboard(user_id))
    else:
        await callback.answer("❌ Hali obuna bo‘lmagansiz!", show_alert=True)

# Callback handler: admin panel
@dp.callback_query(F.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    if callback.from_user.id in ADMIN_IDS:
        await callback.message.edit_text("👑 Admin panelga xush kelibsiz!\n(Hozircha bu yerda hech narsa yo‘q)")
    else:
        await callback.answer("Siz admin emassiz.", show_alert=True)

# Foydalanuvchi anime kodi yuborganda
@dp.message(F.text.regexp(r"^\d+$"))
async def handle_anime_code(message: Message):
    user_id = message.from_user.id
    if not await is_subscribed(user_id):
        await message.answer("📢 Kod yuborishdan oldin kanalga obuna bo‘ling!", reply_markup=subscription_keyboard())
        return

    code = message.text.strip()
    if code in anime_posts:
        post = anime_posts[code]
        await bot.copy_message(chat_id=message.chat.id, from_chat_id=post["channel"], message_id=post["message_id"])
    else:
        await message.answer("❌ Bunday kod topilmadi. Qaytadan urinib ko‘ring.")

# Botni ishga tushirish
async def main():
    logging.basicConfig(level=logging.INFO)
    # keep_alive() agar kerak bo‘lsa shu yerda chaqiriladi
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
