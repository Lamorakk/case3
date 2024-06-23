import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.dispatcher import router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.payload import decode_payload

from config import TOKEN, CHANNEL_ID, PRIVATE_CHANNEL_ID
from middlewares import CheckMembershipMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
from utils import create_join_and_check_buttons, create_main_menu_buttons, generate_private_link, \
    create_start_earn_buttons, create_user_profile_buttons, create_earn_money
from database import get_pool, get_user, create_user, update_balance, create_withdrawal_request, get_pending_request
from admin import router as admin_router
from company import router as company_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.message.middleware(CheckMembershipMiddleware())
dp.include_router(company_router)
dp.include_router(admin_router)

one_time_links = {}

def check_if_any_payload(command: CommandObject):
    args = command.args
    if args is not None:
        return decode_payload(args)
        # args_decoded = decode_payload(args)

    else:
        return None


@dp.message(CommandStart(deep_link=True))
async def handler(message: Message, command: CommandObject):
    # await state.set_state(UserState.lang_code)
    args = check_if_any_payload(command)
    await message.answer(f"{args}")
    # else:
    #     await message.answer("Problems with your referral ID. Contact your referral issuer or our support")

@dp.message(CommandStart())
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

# @dp.message(CommandStart())
# async def start_command(message: Message):
#     user_id = message.from_user.id
#     user_name = message.from_user.full_name
#     try:
#         chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
#         if chat_member.status in ['member', 'administrator', 'creator']:
#             async with await get_pool() as pool:
#                 user = await get_user(pool, user_id)
#                 if not user:
#                     await create_user(pool, user_id, user_name)
#                     try:
#                         await message.edit_text("Welcome to the channel!")
#                     except Exception as e:
#                         logging.error(e)
#                         await message.answer("Welcome to the channel!")
#                 else:
#                     try:
#                         await message.edit_text("Welcome back!")
#                     except Exception as e:
#                         logging.error(e)
#                         await message.answer("Welcome back!")
#             await proceed_to_main_menu(message)
#         else:
#             await send_join_and_check_buttons(message)
#     except Exception as e:
#         logging.error(e)
#         await message.answer("Произошла ошибка при проверке членства в канале.")
#

async def send_join_and_check_buttons(message: Message):
    keyboard = create_join_and_check_buttons()
    await message.answer("Привіт! Будь ласка, приєднайтесь до нашого каналу, щоб продовжити.", reply_markup=keyboard)

@dp.callback_query(F.data == "check_membership")
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

@dp.callback_query(F.data == "earn_money")
async def earn_money(callback_query: CallbackQuery):
    keyboard = create_earn_money()
    try:
        await callback_query.message.edit_text("Щоб почати заробляти, поповніть баланс і купіть доступ до приватного каналу.", reply_markup=keyboard)
    except Exception as e:
        logging.error(e)
        await callback_query.message.answer("Щоб почати заробляти, поповніть баланс і купіть доступ до приватного каналу.", reply_markup=keyboard)

@dp.callback_query(F.data == "buy_access")
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


@dp.callback_query(F.data == "back_to_main_menu")
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

@dp.callback_query(F.data == "my_profile")
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

@dp.callback_query(F.data == "deposit")
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


@dp.callback_query(F.data == "withdraw")
async def withdraw(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    async with await get_pool() as pool:
        pending_request = await get_pending_request(pool, user_id)
        if pending_request:
            await callback_query.message.answer("Ваш запит на виведення в обробці.")
        else:
            await create_withdrawal_request(pool, user_id)
            await callback_query.message.answer("Ваш запит на виведення відправлено та буде оброблено адміністраторами.")




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
