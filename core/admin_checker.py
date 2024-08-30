from aiogram import Bot
from aiogram.types import ChatMember
import logging

logger = logging.getLogger(__name__)

class AdminChecker:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def check_admin_rights(self, chat_id: int, user_id: int) -> bool:
        try:
            member: ChatMember = await self.bot.get_chat_member(chat_id, user_id)
            return member.is_chat_admin() or member.is_chat_owner()
        except Exception as e:
            logger.error(f"Помилка при перевірці прав адміністратора: {e}", exc_info=True)
            return False

    def get_user_status(self, user_id: int):
        # Тут має бути логіка для визначення статусу користувача (наприклад, Pro, Pro Plus)
        # Це може бути запит до бази даних або до іншого джерела
        # Наприклад, статус може бути отриманий із кешу або профілю користувача
        pass
