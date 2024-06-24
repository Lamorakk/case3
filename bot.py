import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile, Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from aiogram import F
import asyncio

from aiogram.utils.payload import decode_payload

from config import TOKEN, CHANNEL_ID, PRIVATE_CHANNEL_ID
from middlewares import CheckMembershipMiddleware
from referral_tree import send_referral_tree_image
from utils import create_join_and_check_buttons, create_main_menu_buttons, generate_private_link, create_start_earn_buttons, create_user_profile_buttons, create_earn_money
from database import get_pool, get_user, create_user, update_balance, create_withdrawal_request, get_pending_request

bot = Bot(token=TOKEN)
dp = Dispatcher()

router = Router()
dp.include_router(router)

dp.message.middleware(CheckMembershipMiddleware())

one_time_links = {}

def check_if_any_payload(command: CommandObject):
    args = command.args
    if args is not None:
        return decode_payload(args)
    else:
        return None
@router.message(CommandStart(deep_link=True))
async def handler(message: Message, command: CommandObject):
    args = check_if_any_payload(command)
    await message.answer(f"{args}")
@router.message(CommandStart())
async def start_command(message: Message):
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
async def send_join_and_check_buttons(message: Message):
    keyboard = create_join_and_check_buttons()
    await message.answer("Привіт! Будь ласка, приєднайтесь до нашого каналу, щоб продовжити.", reply_markup=keyboard)
@router.callback_query(F.data == "check_membership")
async def process_check_membership(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.full_name
    try:
        chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            async with await get_pool() as pool:
                user = await get_user(pool, user_id)
                if not user:
                    await create_user(pool, user_id, user_name)
                    await callback_query.message.edit_text("Дякую за приєднання! Ви тепер можете продовжити.")
                else:
                    await callback_query.message.edit_text("Welcome back! Ви тепер можете продовжити.")
            await proceed_to_main_menu(callback_query.message)
        else:
            await callback_query.answer("Ви не є учасником каналу. Будь ласка, приєднайтесь до каналу та натисніть кнопку для перевірки знову.")
    except Exception as e:
        logging.error(e)
        await callback_query.message.edit_text("Произошла ошибка при проверке членства в канале.")
async def proceed_to_main_menu(message: Message):
    keyboard = create_main_menu_buttons()
    await message.answer("Ви є учасником каналу! Ви можете продовжити.", reply_markup=keyboard)
@router.callback_query(F.data == "earn_money")
async def earn_money(callback_query: CallbackQuery):
    keyboard = create_earn_money()
    try:
        await callback_query.message.edit_text("Щоб почати заробляти, поповніть баланс і купіть доступ до приватного каналу.", reply_markup=keyboard)
    except Exception as e:
        logging.error(e)
        await callback_query.message.answer("Щоб почати заробляти, поповніть баланс і купіть доступ до приватного каналу.", reply_markup=keyboard)

@router.callback_query(F.data == "buy_access")
async def buy_access(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    private_link = await generate_private_link(bot, PRIVATE_CHANNEL_ID)
    one_time_links[private_link.invite_link] = user_id
    async with await get_pool() as pool:
        user = await get_user(pool, user_id)
        balance = user[2]
        if user:
            if (balance >= 25):
                await update_balance(pool, user_id, -25)
                balance = user[2] - 25
                keyboard = create_start_earn_buttons()
                try:
                    await callback_query.message.edit_text(f"Доступ до приватного каналу: {private_link.invite_link}\n"
                                                           f"Ваш поточний баланс: {balance}",
                                                           reply_markup=keyboard)
                except Exception as e:
                    logging.error(e)
                    await callback_query.message.answer(f"Доступ до приватного каналу: {private_link.invite_link}",
                                                        reply_markup=keyboard)
            else:
                keyboard = create_main_menu_buttons()
                try:
                    await callback_query.message.edit_text("Поповніть баланс з допомогою мого профілю, щоб продовжити",
                                                           reply_markup=keyboard)
                except Exception as e:
                    logging.error(e)
                    await callback_query.message.answer("Поповніть баланс з допомогою мого профілю, щоб продовжити",
                                                        reply_markup=keyboard)
@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback_query: CallbackQuery):
    keyboard = create_main_menu_buttons()
    user_id = callback_query.from_user.id
    async with await get_pool() as pool:
        user = await get_user(pool, user_id)
        balance = user[2]
    try:
        await callback_query.message.edit_text(f"Ваш поточний баланс: {balance}", reply_markup=keyboard)
    except Exception as e:
        logging.error(e)
        await callback_query.message.answer("Ви є учасником каналу! Ви можете продовжити.", reply_markup=keyboard)


@router.callback_query(F.data == "my_profile")
async def my_profile(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    async with await get_pool() as pool:
        user = await get_user(pool, user_id)
        if not user:
            await create_user(pool, user_id, callback_query.from_user.full_name)
            user = await get_user(pool, user_id)
        balance = user[2]
        keyboard = create_user_profile_buttons()
        await callback_query.message.edit_text(f"Ваш профіль. Баланс: {balance}$", reply_markup=keyboard)
@router.callback_query(F.data == "deposit")
async def deposit(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    async with await get_pool() as pool:
        user = await get_user(pool, user_id)
        keyboard = create_earn_money()
        if user:
            await update_balance(pool, user_id, 25)
            balance = user[2] + 25
            try:
                await callback_query.message.edit_text(f"Ваш баланс поповнено на 25$. Ваш поточний баланс: {balance}$", reply_markup= keyboard)
            except Exception as e:
                logging.error(e)
                await callback_query.message(f"Ваш баланс поповнено на 25$. Ваш поточний баланс: {balance}$")
        else:
            await callback_query.message("Користувача не знайдено.")

@router.callback_query(F.data == "withdraw")
async def withdraw(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    async with await get_pool() as pool:
        pending_request = await get_pending_request(pool, user_id)
        if pending_request:
            await callback_query.message.answer("Ваш запит на виведення в обробці.")
        else:
            await create_withdrawal_request(pool, user_id)
            await callback_query.message.answer("Ваш запит на виведення відправлено та буде оброблено адміністраторами.")

@router.callback_query(F.data == "referral_program")
async def referral_program(callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Дерево рефералов", callback_data="referral_tree")],
        [InlineKeyboardButton(text="Баланс", callback_data="referral_balance")],
        [InlineKeyboardButton(text="Поделиться ссылкой", switch_inline_query="")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")]
    ])
    await callback_query.message.edit_text("Выберите опцию:", reply_markup=keyboard)

@router.callback_query(F.data == "referral_tree")
async def referral_tree(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await send_referral_tree_image(bot, user_id)
    await callback_query.answer()

@router.callback_query(F.data == "referral_balance")
async def referral_balance(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    async with await get_pool() as pool:
        user = await get_user(pool, user_id)
        if user:
            level_1_earnings = 50.00  # Replace with actual calculation
            level_2_earnings = 25.00  # Replace with actual calculation
            total_balance = user[2]  # Assuming user[2] is the balance

            balance_info = (
                f"Баланс от рефералов уровня 1: {level_1_earnings}$\n"
                f"Баланс от рефералов уровня 2: {level_2_earnings}$\n"
                f"Ваш общий баланс: {total_balance}$"
            )
            await callback_query.message.edit_text(balance_info)
        else:
            await callback_query.message.edit_text("Користувача не знайдено.")
    await callback_query.answer()


@router.message(F.text == "Информация как это работает")
async def how_it_works(message: Message):
    await message.answer("Інформація про проєкт та як це працює.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
