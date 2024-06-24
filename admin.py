import logging
from aiogram import types, Bot, Dispatcher, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from config import ADMIN_GROUP_ID
from database import get_pool, get_pending_orders, update_order_status, get_user

router = Router()

def create_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Start Review Withdraws", callback_data="start_review_withdraws")],
        [InlineKeyboardButton(text="View All History", callback_data="view_all_history")]
    ])

@router.message(lambda message: message.chat.id == ADMIN_GROUP_ID and message.text == "Admin Panel")
async def show_admin_menu(message: Message):
    keyboard = create_admin_keyboard()
    await message.answer("Welcome to the admin panel. Choose an option:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "start_review_withdraws")
async def start_review_withdraws(callback_query: CallbackQuery):
    async with await get_pool() as pool:
        orders = await get_pending_orders(pool)
        if orders:
            await show_order(callback_query, orders[0], 0, orders)
        else:
            await callback_query.message.edit_text("No pending withdrawal requests.")

async def show_order(callback_query: CallbackQuery, order, index, orders):
    user_id = order[1]
    amount = order[2]
    async with await get_pool() as pool:
        user = await get_user(pool, user_id)
        user_name = user[1]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Approve", callback_data=f"approve_{index}")],
        [InlineKeyboardButton(text="Deny", callback_data=f"deny_{index}")],
        [InlineKeyboardButton(text="Previous", callback_data=f"previous_{index}") if index > 0 else None],
        [InlineKeyboardButton(text="Next", callback_data=f"next_{index + 1}") if index < len(orders) - 1 else None]
    ])
    await callback_query.message.edit_text(f"Reviewing withdrawal request №{index + 1}\n\nUser: {user_name} (ID: {user_id})\nAmount: {amount}$", reply_markup=keyboard)

@router.callback_query(lambda c: c.data.startswith("approve_"))
async def approve_withdraw(callback_query: CallbackQuery):
    index = int(callback_query.data.split("_")[1])
    async with await get_pool() as pool:
        orders = await get_pending_orders(pool)
        order = orders[index]
        await update_order_status(pool, order[0], 'approved')
        await callback_query.message.edit_text(f"Withdrawal request №{index + 1} approved.")
        if index < len(orders) - 1:
            await show_order(callback_query, orders[index + 1], index + 1, orders)

@router.callback_query(lambda c: c.data.startswith("deny_"))
async def deny_withdraw(callback_query: CallbackQuery):
    index = int(callback_query.data.split("_")[1])
    async with await get_pool() as pool:
        orders = await get_pending_orders(pool)
        order = orders[index]
        await update_order_status(pool, order[0], 'denied')  # Assuming order_id is the first column
        await callback_query.message.edit_text(f"Withdrawal request №{index + 1} denied.")
        if index < len(orders) - 1:
            await show_order(callback_query, orders[index + 1], index + 1, orders)

@router.callback_query(lambda c: c.data.startswith("next_"))
async def next_order(callback_query: CallbackQuery):
    index = int(callback_query.data.split("_")[1])
    async with await get_pool() as pool:
        orders = await get_pending_orders(pool)
        await show_order(callback_query, orders[index], index, orders)

@router.callback_query(lambda c: c.data.startswith("previous_"))
async def previous_order(callback_query: CallbackQuery):
    index = int(callback_query.data.split("_")[1]) - 1
    async with await get_pool() as pool:
        orders = await get_pending_orders(pool)
        await show_order(callback_query, orders[index], index, orders)

@router.callback_query(lambda c: c.data == "view_all_history")
async def view_all_history(callback_query: CallbackQuery):
    # Placeholder for history viewing logic
    await callback_query.message.edit_text("Displaying all history (to be implemented).")
