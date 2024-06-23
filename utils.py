#utils.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_LINK
from aiogram import Bot

def create_join_and_check_buttons():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Приєднатися до каналу", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="Я приєднався до каналу", callback_data="check_membership")]
    ])
    return keyboard

def create_main_menu_buttons():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать зарабатывать", callback_data="earn_money")],
        [InlineKeyboardButton(text="Реферальная программа", callback_data="referral_program")],
        [InlineKeyboardButton(text="Мой профиль", callback_data="my_profile")],
        [InlineKeyboardButton(text="Информация как это работает", callback_data="how_it_works")]
    ])
    return keyboard
def create_start_earn_buttons():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Купить доступ за 25$",callback_data = "buy_access")],
        [InlineKeyboardButton(text="Назад", callback_data = "back_to_main_menu")]
    ])
    return keyboard


def create_user_profile_buttons():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поповнити баланс", callback_data="deposit")],
        [InlineKeyboardButton(text="Запит на виведення", callback_data="withdraw")],
        [InlineKeyboardButton(text="Посмотреть историю", callback_data="history_us")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")]
    ])
    return keyboard


def create_earn_money():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Купити доступ за 25$", callback_data="buy_access")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")]
    ])
    return keyboard


async def generate_private_link(bot: Bot, private_channel_id: int):
    invite_link = await bot.create_chat_invite_link(private_channel_id, expire_date=None, member_limit=1)
    return invite_link
