import asyncio
import logging
import os
from typing import Final

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

# =========================================================
# ANONYMOUS TELEGRAM RELAY BOT
# =========================================================
# You write to the bot -> bot anonymously sends to colleague
# Colleague writes to the bot -> bot anonymously sends to you
# =========================================================

BOT_TOKEN: Final[str] = "8541743527:AAEDm4CURKpWTvL7lT5GlvU4HGIv0d3FARg"

# Replace with real Telegram user IDs
USER_A_ID: Final[int] = int(os.getenv("USER_A_ID", "13552746"))
USER_B_ID: Final[int] = int(os.getenv("USER_B_ID", "1055114468"))

SUCCESS_TEXT: Final[str] = "Отправлено анонимно ✅"
DENIED_TEXT: Final[str] = "У вас нет доступа к этому боту."

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()


def get_receiver(sender_id: int):
    if sender_id == USER_A_ID:
        return USER_B_ID
    if sender_id == USER_B_ID:
        return USER_A_ID
    return None


def is_allowed(user_id: int):
    return user_id in {USER_A_ID, USER_B_ID}


@dp.message(Command("start"))
async def start_handler(message: Message):
    user = message.from_user
    if not user or not is_allowed(user.id):
        await message.answer(DENIED_TEXT)
        return

    await message.answer(
        "Бот активен.\n"
        "Напишите сообщение, фото, видео или файл — "
        "я анонимно передам это второй стороне."
    )


@dp.message(Command("id"))
async def id_handler(message: Message):
    user = message.from_user
    if not user:
        return
    await message.answer(f"Ваш Telegram user_id: <code>{user.id}</code>")


@dp.message()
async def relay_handler(message: Message):
    user = message.from_user
    if not user:
        return

    sender_id = user.id
    receiver_id = get_receiver(sender_id)

    if receiver_id is None:
        await message.answer(DENIED_TEXT)
        return

    try:
        await bot.copy_message(
            chat_id=receiver_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )

        await message.answer(SUCCESS_TEXT)

    except Exception as e:
        logging.exception(e)
        await message.answer("Ошибка отправки.")


async def main():
    if not BOT_TOKEN:
        raise ValueError("Не указан BOT_TOKEN.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
