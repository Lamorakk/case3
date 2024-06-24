import logging
from aiogram import types, Router, F
from aiogram.client import bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

from bot import proceed_to_main_menu, send_join_and_check_buttons
from config import TOKEN, CHANNEL_ID
from database import get_pool, get_user, create_user, update_balance

router = Router()


def generate_referral_link(user_id):
    return f"https://t.me/YourBot?start={user_id}"

@router.message(CommandStart(deep_link=True))
async def handler(message: Message, command: CommandStart.CommandObject):
    referrer_id = command.args
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    try:
        chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            async with await get_pool() as pool:
                user = await get_user(pool, user_id)
                if not user:
                    await create_user(pool, user_id, user_name)
                    try:
                        await message.edit_text("Welcome to the channel!")
                    except Exception as e:
                        logging.error(e)
                        await message.answer("Welcome to the channel!")
                else:
                    try:
                        await message.edit_text("Welcome back!")
                    except Exception as e:
                        logging.error(e)
                        await message.answer("Welcome back!")
            await proceed_to_main_menu(message)
        else:
            await send_join_and_check_buttons(message)
    except Exception as e:
        logging.error(e)
        await message.answer("Произошла ошибка при проверке членства в канале.")

    async with await get_pool() as pool:
        user = await get_user(pool, user_id)
        if not user:
            await create_user(pool, user_id, user_name, referrer_id)
            user = await get_user(pool, user_id)

        if referrer_id and referrer_id != str(user_id):
            referrer_user = await get_user(pool, referrer_id)
            if referrer_user:
                balance = user[2]
                await update_balance(pool, referrer_id, balance + 0.4 * balance)

                # Get second level referrer if exists
                second_level_referrer_id = referrer_user[3]
                if second_level_referrer_id:
                    balance = user[2]
                    await update_balance(pool, second_level_referrer_id, balance + 0.1 * balance)

@router.message(F.text == "Реферальная программа")
async def referral_program(message: Message):
    user_id = message.from_user.id
    referral_link = generate_referral_link(user_id)
    await message.answer(f"Ваша реферальная ссилка: {referral_link}")


