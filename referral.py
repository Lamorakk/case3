import logging
from aiogram import types, Router, F
from aiogram.client import bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

from bot import proceed_to_main_menu, send_join_and_check_buttons
from config import TOKEN, CHANNEL_ID
from database import get_pool, get_user, create_user, update_balance

# router = Router()
#
#
# def generate_referral_link(user_id):
#     return f"https://t.me/YourBot?start={user_id}"
#
# @router.message(F.text == "Реферальная программа")
# async def referral_program(message: Message):
#     user_id = message.from_user.id
#     referral_link = generate_referral_link(user_id)
#     await message.answer(f"Ваша реферальная ссилка: {referral_link}")
#
#
