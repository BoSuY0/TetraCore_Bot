from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from .pinger_module import zaz_all

def setup_pinger(router: Router, module_manager):
    @router.message(Command("zaz_all"))
    async def zaz_all_handler(message: Message):
        await zaz_all(message, module_manager, message.bot)
