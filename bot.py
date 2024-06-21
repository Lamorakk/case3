
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from config import TOKEN, CHANNEL_ID, PRIVATE_CHANNEL_ID
from middlewares import CheckMembershipMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
from utils import create_join_and_check_buttons, create_main_menu_buttons, generate_private_link

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.message.middleware(CheckMembershipMiddleware())

one_time_links = {}

@dp.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id
    try:
        chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            await proceed_to_main_menu(message)
        else:
            await send_join_and_check_buttons(message)
    except Exception as e:
        logging.error(e)
        await message.answer("Произошла ошибка при проверке членства в канале.")

async def send_join_and_check_buttons(message: Message):
    keyboard = create_join_and_check_buttons()
    await message.answer("Привіт! Будь ласка, приєднайтесь до нашого каналу, щоб продовжити.", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "check_membership")
async def process_check_membership(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            await callback_query.message.edit_text("Дякую за приєднання! Ви тепер можете продовжити.")
            await proceed_to_main_menu(callback_query.message)
        else:
            await callback_query.answer("Ви не є учасником каналу. Будь ласка, приєднайтесь до каналу та натисніть кнопку для перевірки знову.")
    except Exception as e:
        logging.error(e)
        await callback_query.message.edit_text("Произошла ошибка при проверке членства в канале.")

async def proceed_to_main_menu(message: Message):
    keyboard = create_main_menu_buttons()
    await message.answer("Ви є учасником каналу! Ви можете продовжити.", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "earn_money")
async def earn_money(callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Купити доступ за 25$", callback_data="buy_access")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")]
    ])
    try:
        await callback_query.message.edit_text("Щоб почати заробляти, поповніть баланс і купіть доступ до приватного каналу.", reply_markup=keyboard)
    except Exception as e:
        logging.error(e)
        await callback_query.message.answer("Щоб почати заробляти, поповніть баланс і купіть доступ до приватного каналу.", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "buy_access")
async def buy_access(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    private_link = await generate_private_link(bot, PRIVATE_CHANNEL_ID)
    one_time_links[private_link.invite_link] = user_id
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти до приватного каналу", url=private_link.invite_link)],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")]
    ])
    try:
        await callback_query.message.edit_text(f"Доступ до приватного каналу: {private_link.invite_link}", reply_markup=keyboard)
    except Exception as e:
        logging.error(e)
        await callback_query.message.answer(f"Доступ до приватного каналу: {private_link.invite_link}", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "back_to_main_menu")
async def back_to_main_menu(callback_query: CallbackQuery):
    keyboard = create_main_menu_buttons()
    try:
        await callback_query.message.edit_text("Ви є учасником каналу! Ви можете продовжити.", reply_markup=keyboard)
    except Exception as e:
        logging.error(e)
        await callback_query.message.answer("Ви є учасником каналу! Ви можете продовжити.", reply_markup=keyboard)

@dp.message(F.text == "Мой профиль")
async def my_profile(message: Message):
    await message.answer("Ваш профиль. Баланс: 0$")

@dp.message(F.text == "Реферальная программа")
async def referral_program(message: Message):
    await message.answer("Ваша реферальна ссилка: https://t.me/YourBot?start=referral_code")

@dp.message(F.text == "Информация как это работает")
async def how_it_works(message: Message):
    await message.answer("Інформація про проєкт та як це працює.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
