#middlewares.py
import logging
from aiogram import BaseMiddleware
from aiogram.types import Message
from config import CHANNEL_ID
from utils import create_join_and_check_buttons

class CheckMembershipMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        user_id = event.from_user.id
        bot = data['bot']

        try:
            chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
            if chat_member.status in ['member', 'administrator', 'creator']:
                return await handler(event, data)
            else:
                await event.answer("Вы не являетесь членом канала. Пожалуйста, приєднайтесь до каналу, чтобы продолжить.",
                                   reply_markup=create_join_and_check_buttons())
        except Exception as e:
            logging.error(e)
            await event.answer("Произошла ошибка при проверке членства в канале.")
